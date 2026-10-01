"""Small integrity experiments for G0A-T03; no physics calculation."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import random
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from common import ROOT, git_info, read_data, sha256
from configuration import CONFIGS, REGISTRY, load_config
from provenance import check_environment_freeze, freeze, run_identity, seal_run, seed_policy, verify_run


def cpu_environment_smoke():
    """Exercise installed native libraries on small temporary fixtures."""
    import numpy as np
    import scipy.integrate
    import h5py
    with tempfile.TemporaryDirectory() as folder:
        root=Path(folder)
        with h5py.File(root/'fixture.h5','w') as stream:
            stream.create_dataset('values',data=np.arange(12,dtype=np.float64))
        with h5py.File(root/'fixture.h5','r') as stream:
            hdf5_ok=np.array_equal(stream['values'][:],np.arange(12,dtype=np.float64))
        solution=scipy.integrate.solve_ivp(lambda t,y:-y,(0,1),[1.],rtol=1e-10,atol=1e-12)
        ode_error=float(abs(solution.y[0,-1]-np.exp(-1)))
        previous=os.environ.get('MPLCONFIGDIR')
        os.environ['MPLCONFIGDIR']=str(root/'matplotlib')
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_agg import FigureCanvasAgg
            figure=Figure(figsize=(1,1),dpi=32)
            figure.add_subplot().plot([0,1],[0,1])
            FigureCanvasAgg(figure).print_png(root/'fixture.png')
            render_ok=(root/'fixture.png').read_bytes().startswith(b'\x89PNG\r\n\x1a\n')
        finally:
            if previous is None:
                os.environ.pop('MPLCONFIGDIR',None)
            else:
                os.environ['MPLCONFIGDIR']=previous
    dependencies=subprocess.run([sys.executable,'-m','pip','--disable-pip-version-check','--no-cache-dir','check'],capture_output=True,text=True)
    return {'hdf5_float64_roundtrip':bool(hdf5_ok),'scipy_exponential_ode_abs_error':ode_error,
            'matplotlib_agg_png_rendered':render_ok,'pip_check_exit_code':dependencies.returncode,
            'pip_check_output':dependencies.stdout.strip()}


def validate_discipline(config):
    import numpy as np
    validated = [load_config(ROOT/relative)[0]["task"] for relative,_ in CONFIGS.values()]
    distributions = check_environment_freeze(ROOT/config["parameters"]["environment_freeze"])
    smoke=cpu_environment_smoke()
    fingerprints = {}
    reproducible = True
    for seed in config["seeds"]:
        scoped = dict(config,seeds=[seed])
        draws = []
        for _ in range(2):
            seed_policy(scoped)
            value = (np.random.default_rng(seed).normal(size=32).tobytes()
                     + np.random.random(32).tobytes() + repr([random.random() for _ in range(32)]).encode())
            draws.append(hashlib.sha256(value).hexdigest())
        reproducible &= draws[0] == draws[1]
        fingerprints[str(seed)] = draws[0]
    seed_policy(config)
    separate_seeds = len(set(fingerprints.values())) == len(fingerprints)
    with tempfile.TemporaryDirectory() as folder:
        run = Path(folder)
        for name in ("config.yaml","metadata.json","environment.json","result.json"):
            freeze(run/name,{"fixture":True,"name":name})
        (run/"validation.log").write_text("integrity fixture\n")
        seal_run(run)
        initial_seal = verify_run(run)
        protected = False
        try:
            freeze(run/"metadata.json",{"fixture":"overwrite"})
        except FileExistsError:
            protected = True
        (run/"result.json").chmod(0o644)
        (run/"result.json").write_text('{"fixture":"tampered"}\n')
        tamper_detected = False
        try:
            verify_run(run)
        except ValueError:
            tamper_detected = True
    commit = git_info(ROOT)["git_commit"]
    identity = run_identity(config["task"],config["machine"],datetime.now(timezone.utc),commit,
                            sha256(ROOT/CONFIGS[(config["task"],config["machine"])][0]))
    checks = {"all_frozen_configs_match":len(validated)==len(CONFIGS),
              "full_environment_matches":distributions>0,
              "same_seeds_reproduce":reproducible,"different_seeds_differ":separate_seeds,
              "metadata_overwrite_rejected":protected,"tampered_result_rejected":tamper_detected,
              "run_identity_has_required_parts":len(identity.split('__'))==5,
              "cpu_native_libraries_work":smoke['hdf5_float64_roundtrip'] and smoke['scipy_exponential_ode_abs_error']<1e-8 and smoke['matplotlib_agg_png_rendered'],
              "pip_dependencies_coherent":smoke['pip_check_exit_code']==0}
    return {"passed":all(checks.values()),"checks":checks,"configs_checked":len(validated),
            "resolved_distributions":distributions,"seed_fingerprints":fingerprints,
            "cpu_environment_smoke":smoke,
            "temporary_integrity_fixture_seal":initial_seal,
            "physics_gate_evaluated":False,"cuda_verified":False}
