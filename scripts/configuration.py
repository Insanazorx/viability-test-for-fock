"""Validate and explicitly freeze predeclared configurations by exact bytes."""
from __future__ import annotations

import argparse
import hashlib
import sys

from common import ROOT, decode_data, inside, read_data, sha256, write_data

CONFIGS = {
    ("G0A-T01", "MACM6"): ("config/benchmark/g0a_t01.json.yaml", "validate_repository"),
    ("G0A-T02", "MACM6"): ("config/benchmark/g0a_t02_macm6.json.yaml", "validate_math_core"),
    ("G0A-T02", "RTX5070"): ("config/benchmark/g0a_t02_rtx5070.json.yaml", "validate_math_core_cuda"),
    ("G0A-T03", "MACM6"): ("config/benchmark/g0a_t03_macm6.json.yaml", "validate_run_discipline"),
}
REGISTRY = "config/frozen_registry.yaml"


def validate_config(config, root=ROOT):
    from jsonschema import Draft202012Validator
    schema = read_data(root / "config/schema.yaml")
    Draft202012Validator.check_schema(schema)
    violations = sorted(Draft202012Validator(schema).iter_errors(config), key=lambda e: str(e.path))
    if violations:
        raise ValueError("Invalid config: " + "; ".join(error.message for error in violations))
    record = CONFIGS.get((config["task"], config["machine"]))
    if not record or config["parameters"].get("handler") != record[1]:
        raise ValueError("No predeclared handler for this task/machine")
    if config["parameters"].get("allow_cloud") is not False:
        raise ValueError("These predeclared handlers do not permit cloud execution")
    if config["kind"] == "numerical" and config["precision"] == "N/A":
        raise ValueError("Numerical runs require an explicit precision")
    if not isinstance(config["parameters"].get("minimum_tests"), int) or isinstance(config["parameters"]["minimum_tests"], bool) or config["parameters"]["minimum_tests"] <= 0:
        raise ValueError("A positive minimum test count is required")
    if config["task"] == "G0A-T02":
        if config["precision"] != "float64" or config["kind"] != "numerical":
            raise ValueError("The core acceptance configs require float64 numerics")
        expected_tolerances = ({"identity_normalized", "rotation_normalized", "gradient_normalized", "reduction_normalized"}
                               if config["machine"] == "MACM6" else {"backend_normalized", "autograd_normalized"})
        if set(config["tolerances"]) != expected_tolerances:
            raise ValueError("Required core tolerances are absent")
        for key in ("samples_per_seed", "rotations_per_seed"):
            if key in config["parameters"] and (type(config["parameters"][key]) is not int or config["parameters"][key] <= 0):
                raise ValueError("Sample/rotation counts must be positive integers")
    elif config["kind"] != "control" or config["precision"] != "N/A":
        raise ValueError("Infrastructure handlers require control/N/A")
    return record


def freeze_configs(root=ROOT):
    entries = {}
    for (task, machine), (relative, handler) in CONFIGS.items():
        path = inside(root, relative, "config")
        config = read_data(path)
        validate_config(config, root)
        entries[f"{task}/{machine}"] = {"path": relative, "handler": handler, "sha256": sha256(path)}
    registry = {"schema_version": 1, "entries": entries,
                "policy": "Exact byte hashes; changed configs require explicit freeze and commit before acceptance runs"}
    write_data(root / REGISTRY, registry)
    return registry


def load_config(path, root=ROOT):
    raw = path.read_bytes()
    config = decode_data(raw)
    record = validate_config(config, root)
    relative = path.resolve().relative_to(root.resolve()).as_posix()
    if relative != record[0]:
        raise ValueError("Use the canonical predeclared config path")
    registry = read_data(root / REGISTRY)
    entry = registry["entries"].get(f"{config['task']}/{config['machine']}")
    digest = hashlib.sha256(raw).hexdigest()
    if not entry or entry["path"] != relative or entry["handler"] != record[1] or entry["sha256"] != digest:
        raise ValueError("Frozen config changed; review, explicitly freeze and commit before running")
    return config, raw, digest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("freeze", "check"))
    args = parser.parse_args()
    try:
        if args.action == "freeze":
            result = freeze_configs()
            print(f"Explicitly froze {len(result['entries'])} configs. Commit registry/configs before acceptance runs.")
        else:
            for relative, _ in CONFIGS.values():
                load_config(ROOT / relative)
            print("All frozen config hashes match.")
    except (ValueError, KeyError, OSError) as error:
        print(f"configuration: {error}", file=sys.stderr)
        raise SystemExit(1)
