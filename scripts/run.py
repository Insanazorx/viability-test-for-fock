"""Identified predeclared setup/math-core validation; no lattice solver is installed."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import platform
import re
import subprocess
import sys
import time

from common import ROOT, git_info, inside, read_data, sha256
from ctl import ensure_machine_ready, validate
from configuration import load_config, REGISTRY
from provenance import (RamMonitor, check_environment_freeze, freeze, hardware,
                        packages, run_identity, seal_run, seed_policy)

DIRECTORIES = ["state", "config/benchmark", *(f"config/gate{i}" for i in range(1, 7)),
               *(f"src/{s}" for s in ("core", "static", "hessian", "dynamics", "cosmology", "analysis")),
               *(f"tests/{s}" for s in ("unit", "reference", "regression")),
               "scripts", "runs", "checkpoints", *(f"reports/G{i}" for i in range(7)), "docs"]
FILES = ["AGENTS.md", "STATUS.md", "NEXT.md", "MACHINE_HANDOFF.md", ".gitignore",
         "pyproject.toml", "config/schema.yaml", "state/state.yaml", "reports/SUBSTEP_REPORT_TEMPLATE.md",
         "docs/RUNBOOK.md", *(f"docs/{m}_CHECKLIST.md" for m in ("MACM6", "RTX5070", "CLOUD"))]


def version(package: str) -> str | None:
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--check", action="store_true", help="Read-only config/device preflight; creates no run")
    args = parser.parse_args()
    if sys.version_info[:2] != (3, 12):
        raise ValueError("Python 3.12 is required")
    config_path = inside(ROOT, args.config, "config")
    config, raw, digest = load_config(config_path)
    observed_hardware = hardware(config["machine"])
    if args.check:
        print(json.dumps({"config_sha256":digest,"hardware":observed_hardware,"preflight":"PASS"}))
        return 0
    state = read_data(ROOT / "state/state.yaml")
    validate(state)
    task = ensure_machine_ready(state, config["task"], config["machine"])
    if task["status"] not in {"CLAIMED", "RUNNING"}:
        raise ValueError("Start the task before launching a run")
    inputs = {REGISTRY:sha256(ROOT/REGISTRY),"config/schema.yaml":sha256(ROOT/"config/schema.yaml")}
    if config["task"] in {"G0A-T02","G0B-T01","G0B-T02","G4A-T01"}:
        manifest_path = inside(ROOT, config["parameters"]["source_manifest"], "config")
        manifest = read_data(manifest_path)
        publication = inside(ROOT, manifest["path"])
        expected_hash = config["parameters"]["source_sha256"]
        if not manifest["bibliographic_identity_verified"] or sha256(publication) != manifest["sha256"] or manifest["sha256"] != expected_hash:
            raise ValueError("Publication identity/hash changed; resolve before running")
        inputs.update({manifest["path"]: expected_hash,
                  manifest_path.relative_to(ROOT).as_posix(): sha256(manifest_path),
                  "docs/MATH_CORE.md": sha256(ROOT / "docs/MATH_CORE.md")})
        if config['task'] in {'G0B-T01','G0B-T02'}:
            inputs['docs/G0B_SPECTRAL.md']=sha256(ROOT/'docs/G0B_SPECTRAL.md')
        if config['task']=='G0B-T02':
            inputs['docs/G0B_HOPF.md']=sha256(ROOT/'docs/G0B_HOPF.md')
        if config['task']=='G4A-T01':
            inputs['docs/G4A_OPERATOR_BASIS.md']=sha256(ROOT/'docs/G4A_OPERATOR_BASIS.md')
    if config["parameters"].get("environment_freeze"):
        path = inside(ROOT, config["parameters"]["environment_freeze"], "requirements")
        # The historical G0A-T02 NumPy-only freeze remains an immutable input, not the new full environment lock.
        if config["task"] == "G0A-T03" or (config['task'] in {'G0B-T01','G0B-T02','G4A-T01'} and config['machine']=='MACM6'):
            check_environment_freeze(path)
        inputs[path.relative_to(ROOT).as_posix()] = sha256(path)
    recovery = task.get("recovery")
    if recovery:
        for name in ("previous_failure_report", "previous_environment_freeze"):
            path = inside(ROOT, recovery[name])
            inputs[path.relative_to(ROOT).as_posix()] = sha256(path)
    prerequisites=task.get('machine_prerequisites',{}).get(config['machine'],[{'task':dep} for dep in task['prerequisites']])
    for requirement in prerequisites:
        dependency=state['tasks'][requirement['task']]
        machines=[requirement['machine']] if 'machine' in requirement else dependency['machine_order']
        for machine in machines:
            path=inside(ROOT,dependency['machine_reports'][machine],'reports')
            inputs[path.relative_to(ROOT).as_posix()]=sha256(path)
    started = datetime.now(timezone.utc)
    start = time.perf_counter()
    git = git_info(ROOT)
    run_id = run_identity(config["task"],config["machine"],started,git["git_commit"],digest)
    checkpoint_path=ROOT/'checkpoints'/f'{run_id}__initial.h5' if config['task']=='G0B-T02' else None
    run = ROOT / "runs" / run_id
    run.mkdir()  # Exclusive creation: never overwrite an existing run.
    with (run / "config.yaml").open("xb") as stream:
        stream.write(raw)
    (run / "config.yaml").chmod(0o444)
    freeze(run / "environment.json", {"python": platform.python_version(), "packages": packages()})
    inputs["environment.json"] = sha256(run / "environment.json")
    metadata = {"run_id": run_id, "task": config["task"], "machine": config["machine"],
                **git, "config_sha256": digest, "config_path": args.config,
                "started_utc": started.isoformat(), "os": platform.platform(),
                "architecture": platform.machine(), "python": platform.python_version(),
                "python_executable": sys.executable,
                "pytorch": version("torch"), "cuda": observed_hardware.get("cuda_runtime"),
                "cuda_note": "No CUDA execution on MACM6; measured inside RTX5070 handler",
                "numpy": version("numpy"), "input_sha256": inputs,
                "precision": config["precision"], "seeds": config["seeds"],
                **{k: config[k] for k in ("grid", "box", "time_step", "optimizer", "integrator", "tolerances")},
                "checkpoint_sha256": None, "hardware_role": config["machine"],
                "hardware":observed_hardware,"seed_policy":seed_policy(config),
                "integrity_schema_version":1,
                "recovery":recovery,
                "prerequisite_scope":prerequisites,
                "machine_scheduling":state.get('machine_scheduling',{}),
                "checkpoint_output":checkpoint_path.relative_to(ROOT).as_posix() if checkpoint_path else None,
                "precision_policy":"explicit declared dtype; no MPS acceptance or implicit mixed precision"}
    freeze(run / "metadata.json", metadata)
    metrics = {}
    ram_monitor = RamMonitor().start()
    try:
        missing = [p for p in DIRECTORIES if not (ROOT / p).is_dir()]
        missing += [p for p in FILES if not (ROOT / p).is_file()]
        metrics["layout_complete"] = not missing
        metrics["missing_paths"] = missing
        with (run / "validation.log").open("x", encoding="utf-8") as log:
            tests = subprocess.Popen([sys.executable, "-m", "unittest", "discover", "-s", "tests/unit", "-v"],
                                     cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
            ram_monitor.watch(tests.pid)
            returncode=tests.wait()
            ram_monitor.unwatch(tests.pid)
        metrics["tests_exit_code"] = returncode
        count = re.search(r"Ran (\d+) tests? in", (run / "validation.log").read_text(encoding="utf-8"))
        metrics["tests_run"] = int(count.group(1)) if count else 0
        metrics["minimum_tests"] = config["parameters"]["minimum_tests"]
        metrics["state_valid"] = True
        metrics["cloud_paused"] = state["cloud"]["paused"]
        metrics["cloud_budget_usd"] = state["cloud"]["max_usd_per_run"]
        metrics["publication_present"] = (ROOT / "yayınlanan.pdf").is_file()
        if config["task"] == "G0A-T02":
            sys.path.insert(0, str(ROOT / "src"))
            if config["machine"] == "MACM6":
                from analysis.validate_core import validate_core
                metrics["math_core"] = validate_core(config)
            else:
                from analysis.validate_cuda import validate_cuda
                metrics["math_core"] = validate_cuda(config)
        if config["task"] == "G0A-T03":
            from validate_discipline import validate_discipline
            metrics["run_discipline"] = validate_discipline(config)
        if config['task']=='G0B-T01':
            sys.path.insert(0,str(ROOT/'src'))
            from analysis.validate_spectral import validate_spectral
            metrics['spectral']=validate_spectral(config)
        if config['task']=='G0B-T02':
            sys.path.insert(0,str(ROOT/'src'))
            from analysis.validate_hopf import validate_hopf
            metrics['hopf']=validate_hopf(config,checkpoint_path,run_id,digest)
        if config['task']=='G4A-T01':
            sys.path.insert(0,str(ROOT/'src'))
            from analysis.validate_operators import validate_operators
            metrics['operator_basis']=validate_operators(config)
        status = "PASS" if (not missing and returncode == 0 and state["cloud"]["paused"]
                            and metrics["tests_run"] >= metrics["minimum_tests"]
                            and metrics.get("math_core", {"passed": True})["passed"]
                            and metrics.get("run_discipline", {"passed": True})["passed"]
                            and metrics.get('spectral',{'passed':True})['passed']
                            and metrics.get('hopf',{'passed':True})['passed']
                            and metrics.get('operator_basis',{'passed':True})['passed']) else "FAIL"
        anomaly = None
    except Exception as error:
        status, anomaly = "FAIL", f"{type(error).__name__}: {error}"
    result = {"run_id": run_id, "status": status, "finished_utc": datetime.now(timezone.utc).isoformat(),
              "wall_time_seconds": time.perf_counter() - start, **ram_monitor.finish(),
              "peak_vram_gb": metrics.get('hopf',metrics.get("spectral",metrics.get("math_core", {}))).get("peak_vram_gb"),
              "checkpoint_sha256":sha256(checkpoint_path) if checkpoint_path and checkpoint_path.is_file() else None,
              "checkpoint_path":checkpoint_path.relative_to(ROOT).as_posix() if checkpoint_path and checkpoint_path.is_file() else None,
              "metrics": metrics, "anomaly": anomaly}
    freeze(run / "result.json", result)
    seal_run(run)
    print(json.dumps({"run_id": run_id, "status": status, "metrics": metrics}, ensure_ascii=False))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError, ImportError) as error:
        print(f"run: {error}", file=sys.stderr)
        raise SystemExit(1)
