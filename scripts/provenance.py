"""Portable run identity, exclusive snapshots, integrity checks and RAM sampling."""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import random
import re
import shutil
import subprocess
import threading

from common import inside, read_data, sha256


def freeze(path, value):
    encoded = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    with path.open("x", encoding="utf-8") as stream:
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())
    path.chmod(0o444)


def run_identity(task, machine, started, commit, config_hash):
    if not re.fullmatch(r"G[0-6][A-G]-T\d{2}", task) or machine not in {"MACM6", "RTX5070", "CLOUD"}:
        raise ValueError("Invalid task/machine")
    if not re.fullmatch(r"[a-f0-9]{40}", commit) or not re.fullmatch(r"[a-f0-9]{64}", config_hash):
        raise ValueError("Real commit/config SHA values are required")
    if started.tzinfo is None:
        raise ValueError("Run timestamps must be timezone-aware")
    return f"{task}__{machine}__{started.astimezone(timezone.utc):%Y%m%dT%H%M%SZ}__{commit[:7]}__{config_hash[:8]}"


def packages():
    return dict(sorted((dist.metadata["Name"], dist.version) for dist in importlib.metadata.distributions()))


def check_environment_freeze(path):
    installed = {name.lower().replace('_','-'): version for name,version in packages().items()}
    expected = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        name,version = line.split("==",1)
        expected[name.lower().replace('_','-')] = version
    if expected != installed:
        raise ValueError("Installed packages differ from the frozen environment; review/freeze before running")
    return len(expected)


def seed_policy(config):
    import numpy as np
    first = config["seeds"][0]
    random.seed(first)
    np.random.seed(first)
    policy = {"python_random_seed": first, "numpy_legacy_seed": first,
              "numpy_generator": "explicit default_rng(PCG64) per declared seed",
              "torch_seeded": False, "cross_device_bitwise_identity_required": False}
    if config["machine"] == "RTX5070":
        os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")
        import torch
        torch.manual_seed(first)
        torch.cuda.manual_seed_all(first)
        torch.use_deterministic_algorithms(True)
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.backends.cudnn.allow_tf32 = False
        policy.update(torch_seeded=True, torch_deterministic_algorithms=True,
                      cublas_workspace_config=os.environ["CUBLAS_WORKSPACE_CONFIG"], tf32=False)
    return policy


def hardware(machine):
    import psutil
    try:
        capacity = psutil.virtual_memory().total/1e9
        capacity_note = None
    except (OSError,psutil.AccessDenied) as error:
        capacity,capacity_note = None,str(error)
    value = {"os": platform.platform(), "architecture": platform.machine(),
             "logical_cpu_count": os.cpu_count(), "ram_capacity_gb": capacity,
             "ram_capacity_note":capacity_note,
             "role": machine, "hardware_model": "role label; exact model not attested"}
    if machine == "RTX5070":
        import torch
        if not torch.cuda.is_available():
            raise ValueError("Actual CUDA hardware is required for RTX5070 acceptance")
        properties = torch.cuda.get_device_properties(0)
        value.update(cuda_runtime=torch.version.cuda, pytorch=torch.__version__,
                     cuda_device=torch.cuda.get_device_name(0),
                     cuda_capability=list(torch.cuda.get_device_capability(0)),
                     vram_capacity_gb=properties.total_memory/1e9)
        executable = shutil.which("nvidia-smi")
        if executable:
            value["nvidia_smi"] = subprocess.check_output(
                [executable,"--query-gpu=name,driver_version,memory.total","--format=csv,noheader,nounits"],
                text=True,timeout=10).strip()
        else:
            value["nvidia_smi"] = None
    return value


class RamMonitor:
    """Sample parent and registered children without enumerating host processes."""
    def __init__(self, interval=0.01):
        import psutil
        self.process = psutil.Process()
        self.interval = interval
        self.peak_bytes = 0
        self.samples = 0
        self.children = {}
        self.lock = threading.Lock()
        self.child_sample_errors = 0
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._loop,daemon=True)

    def _sample(self):
        import psutil
        memory = self.process.memory_info().rss
        with self.lock:
            children=list(self.children.values())
        for child in children:
            try:
                memory += child.memory_info().rss
            except (psutil.NoSuchProcess,psutil.AccessDenied,OSError):
                self.child_sample_errors += 1
                continue
        self.peak_bytes = max(self.peak_bytes,memory)
        self.samples += 1

    def _loop(self):
        while not self.stop_event.wait(self.interval):
            self._sample()

    def start(self):
        self._sample()
        self.thread.start()
        return self

    def watch(self,pid):
        import psutil
        with self.lock:
            self.children[pid]=psutil.Process(pid)

    def unwatch(self,pid):
        with self.lock:
            self.children.pop(pid,None)

    def finish(self):
        self.stop_event.set()
        self.thread.join()
        self._sample()
        return {"peak_ram_gb":self.peak_bytes/1e9,
                "peak_ram_method":f"sampled parent+registered-child RSS sum at {self.interval} s; observed peak",
                "ram_samples":self.samples,"child_ram_sample_errors":self.child_sample_errors}


def seal_run(run):
    artifacts = {name:sha256(run/name) for name in
                 ("config.yaml","metadata.json","environment.json","result.json","validation.log")}
    freeze(run/"integrity.json", {"schema_version":1,"artifact_sha256":artifacts})


def verify_run(run):
    seal = read_data(run/"integrity.json")
    required={"config.yaml","metadata.json","environment.json","result.json","validation.log"}
    if seal.get("schema_version") != 1 or set(seal.get("artifact_sha256",{})) != required:
        raise ValueError("Incomplete run integrity manifest")
    for name,digest in seal["artifact_sha256"].items():
        path = inside(run,name)
        if sha256(path) != digest:
            raise ValueError(f"Run evidence changed: {name}")
    return sha256(run/"integrity.json")
