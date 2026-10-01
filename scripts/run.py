"""Identified infrastructure validation run; physics handlers are not installed."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import platform
import re
import resource
import subprocess
import sys
import time

from common import ROOT, git_info, inside, read_data
from ctl import ensure_machine_ready, validate

DIRECTORIES = ["state", "config/benchmark", *(f"config/gate{i}" for i in range(1, 7)),
               *(f"src/{s}" for s in ("core", "static", "hessian", "dynamics", "cosmology", "analysis")),
               *(f"tests/{s}" for s in ("unit", "reference", "regression")),
               "scripts", "runs", "checkpoints", *(f"reports/G{i}" for i in range(7)), "docs"]
FILES = ["AGENTS.md", "STATUS.md", "NEXT.md", "MACHINE_HANDOFF.md", ".gitignore",
         "pyproject.toml", "config/schema.yaml", "state/state.yaml", "reports/SUBSTEP_REPORT_TEMPLATE.md",
         "docs/RUNBOOK.md", *(f"docs/{m}_CHECKLIST.md" for m in ("MACM6", "RTX5070", "CLOUD"))]


def freeze(path, value) -> None:
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    path.chmod(0o444)


def version(package: str) -> str | None:
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 12):
        raise ValueError("Python 3.12 is required")
    config_path = inside(ROOT, args.config, "config")
    raw = config_path.read_bytes()
    config = json.loads(raw)
    schema = read_data(ROOT / "config/schema.yaml")
    # G0A-T01 has one frozen, predeclared configuration. Full numerical parsing is G0A-T03.
    if set(config) != set(schema["required"]) or config != read_data(ROOT / "config/benchmark/g0a_t01.json.yaml"):
        raise ValueError("Only the predeclared G0A-T01 control configuration is supported")
    if (config["task"], config["machine"], config["kind"]) != ("G0A-T01", "MACM6", "control"):
        raise ValueError("No handler is installed for this task/machine")
    state = read_data(ROOT / "state/state.yaml")
    validate(state)
    task = ensure_machine_ready(state, config["task"], config["machine"])
    if task["status"] not in {"CLAIMED", "RUNNING"}:
        raise ValueError("Start the task before launching a run")
    started = datetime.now(timezone.utc)
    start = time.perf_counter()
    digest = hashlib.sha256(raw).hexdigest()
    git = git_info(ROOT)
    run_id = f"{config['task']}__{config['machine']}__{started:%Y%m%dT%H%M%SZ}__{git['git_commit'][:7]}__{digest[:8]}"
    run = ROOT / "runs" / run_id
    run.mkdir()  # Exclusive creation: never overwrite an existing run.
    (run / "config.yaml").write_bytes(raw)
    (run / "config.yaml").chmod(0o444)
    metadata = {"run_id": run_id, "task": config["task"], "machine": config["machine"],
                **git, "config_sha256": digest, "config_path": args.config,
                "started_utc": started.isoformat(), "os": platform.platform(),
                "architecture": platform.machine(), "python": platform.python_version(),
                "python_executable": sys.executable,
                "pytorch": version("torch"), "cuda": None,
                "cuda_note": "Not queried: MACM6 control validation; no CUDA execution",
                "precision": config["precision"], "seeds": config["seeds"],
                **{k: config[k] for k in ("grid", "box", "time_step", "optimizer", "integrator", "tolerances")},
                "checkpoint_sha256": None, "hardware_role": "MACM6 control",
                "hardware_model": "not measured; role name is not a hardware attestation"}
    freeze(run / "metadata.json", metadata)
    metrics = {}
    try:
        missing = [p for p in DIRECTORIES if not (ROOT / p).is_dir()]
        missing += [p for p in FILES if not (ROOT / p).is_file()]
        metrics["layout_complete"] = not missing
        metrics["missing_paths"] = missing
        with (run / "validation.log").open("x", encoding="utf-8") as log:
            tests = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests/unit", "-v"],
                                   cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        metrics["tests_exit_code"] = tests.returncode
        count = re.search(r"Ran (\d+) tests? in", (run / "validation.log").read_text(encoding="utf-8"))
        metrics["tests_run"] = int(count.group(1)) if count else 0
        metrics["minimum_tests"] = config["parameters"]["minimum_tests"]
        metrics["state_valid"] = True
        metrics["cloud_paused"] = state["cloud"]["paused"]
        metrics["cloud_budget_usd"] = state["cloud"]["max_usd_per_run"]
        metrics["publication_present"] = (ROOT / "yayınlanan.pdf").is_file()
        status = "PASS" if (not missing and tests.returncode == 0 and state["cloud"]["paused"]
                            and metrics["tests_run"] >= metrics["minimum_tests"]) else "FAIL"
        anomaly = None
    except Exception as error:
        status, anomaly = "FAIL", f"{type(error).__name__}: {error}"
    scale = 1e9 if sys.platform == "darwin" else 1e6
    ram = max(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss) / scale
    result = {"run_id": run_id, "status": status, "finished_utc": datetime.now(timezone.utc).isoformat(),
              "wall_time_seconds": time.perf_counter() - start, "peak_ram_gb": ram,
              "peak_ram_method": "maximum process RSS (parent or child), not concurrent aggregate RAM",
              "peak_vram_gb": None, "checkpoint_sha256": None,
              "metrics": metrics, "anomaly": anomaly}
    freeze(run / "result.json", result)
    print(json.dumps({"run_id": run_id, "status": status, "metrics": metrics}, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError) as error:
        print(f"run: {error}", file=sys.stderr)
        raise SystemExit(1)
