"""HDF5 solver state without pickle; restart at completed AL boundaries."""
from __future__ import annotations

import json
import os
from pathlib import Path
import random

import h5py
import numpy as np


def _write(group, value):
    import torch
    if isinstance(value, (dict, list, tuple)):
        group.attrs['kind'] = 'dict' if isinstance(value, dict) else type(value).__name__
        items = value.items() if isinstance(value, dict) else enumerate(value)
        for index, (key, item) in enumerate(items):
            child = group.create_group(str(index))
            child.attrs['key'] = json.dumps(key)
            _write(child, item)
    elif torch.is_tensor(value) or isinstance(value, np.ndarray):
        group.attrs['kind'] = 'tensor' if torch.is_tensor(value) else 'ndarray'
        data = value.detach().cpu().numpy() if torch.is_tensor(value) else value
        group.create_dataset('value', data=data)
    else:
        group.attrs['kind'] = 'scalar'
        group.attrs['value'] = json.dumps(value, allow_nan=False)


def _read(group):
    import torch
    kind = group.attrs['kind']
    if kind == 'scalar':
        return json.loads(group.attrs['value'])
    if kind in {'tensor', 'ndarray'}:
        value = group['value'][()]
        return torch.from_numpy(np.asarray(value)) if kind == 'tensor' else value
    if kind not in {'dict', 'list', 'tuple'}:
        raise ValueError('Unknown checkpoint value type')
    items = [(json.loads(group[key].attrs['key']), _read(group[key]))
             for key in sorted(group.keys(), key=int)]
    if kind == 'dict':
        return dict(items)
    values = [value for _, value in items]
    return tuple(values) if kind == 'tuple' else values


def rng_state():
    import torch
    return {'python': random.getstate(), 'numpy': np.random.get_state(),
            'torch': torch.get_rng_state(),
            'cuda': torch.cuda.get_rng_state_all() if torch.cuda.is_available() else []}


def restore_rng(state):
    import torch
    random.setstate(state['python'])
    np.random.set_state(state['numpy'])
    torch.set_rng_state(state['torch'])
    if state['cuda']:
        torch.cuda.set_rng_state_all(state['cuda'])


def save_checkpoint(path, state, identity):
    path = Path(path)
    if path.exists():
        raise FileExistsError('Solver checkpoints are never overwritten')
    temporary = path.with_suffix(path.suffix + '.tmp')
    try:
        with h5py.File(temporary, 'x') as stream:
            stream.attrs['schema_version'] = 1
            stream.attrs['identity'] = json.dumps(identity, sort_keys=True)
            _write(stream.create_group('state'), state)
            _write(stream.create_group('rng'), rng_state())
            stream.flush()
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def load_checkpoint(path, expected_identity):
    with h5py.File(path, 'r') as stream:
        if stream.attrs.get('schema_version') != 1:
            raise ValueError('Unsupported solver checkpoint schema')
        identity = json.loads(stream.attrs['identity'])
        if any(identity.get(key) != value for key, value in expected_identity.items()):
            raise ValueError('Checkpoint config/code/grid identity mismatch')
        return {'identity': identity, 'state': _read(stream['state']), 'rng': _read(stream['rng'])}
