"""Small standard-library helpers; JSON is the control plane's YAML 1.2 subset."""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
MACHINES = ("MACM6", "RTX5070", "CLOUD")
REPORT_FIELDS = (
    "status", "machine", "git_commit", "config_sha256", "run_ids",
    "started_utc", "finished_utc", "wall_time", "peak_ram_gb",
    "peak_vram_gb", "precision",
)
REPORT_SECTIONS = (
    "Objective", "Inputs", "Numerical method", "Tolerances", "Primary metrics",
    "Convergence checks", "Pass/fail evaluation", "Anomalies", "Artifacts/checkpoints",
    "Reproduction command", "What changed from previous report", "Next action",
    "Handoff references",
)


def decode_data(raw: bytes | str) -> dict:
    """JSON or safe YAML, rejecting duplicate keys and non-finite values."""
    def unique_pairs(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate key: {key}")
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError(f"Non-finite value: {value}")

    try:
        value = json.loads(raw, object_pairs_hook=unique_pairs, parse_constant=reject_constant)
    except json.JSONDecodeError:
        import yaml

        class UniqueSafeLoader(yaml.SafeLoader):
            pass

        def mapping(loader, node):
            return unique_pairs((loader.construct_object(key, deep=True),
                                 loader.construct_object(item, deep=True)) for key, item in node.value)

        UniqueSafeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
        try:
            value = yaml.load(raw, Loader=UniqueSafeLoader)
        except yaml.YAMLError as error:
            raise ValueError(f"Invalid safe YAML: {error}") from error
    def finite(item, seen):
        if isinstance(item, float) and not math.isfinite(item):
            raise ValueError("Non-finite value")
        if isinstance(item, (dict, list)):
            if id(item) in seen:
                raise ValueError("Cyclic YAML alias")
            seen.add(id(item))
            for child in (item.values() if isinstance(item, dict) else item):
                finite(child, seen)
            seen.remove(id(item))
    finite(value, set())
    if not isinstance(value, dict):
        raise ValueError("Expected an object")
    return value


def read_data(path: Path) -> dict:
    return decode_data(path.read_bytes())


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def write_data(path: Path, value: dict) -> None:
    atomic_write(path, json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def inside(root: Path, value: str, prefix: str | None = None) -> Path:
    path = (root / value).resolve()
    path.relative_to(root.resolve())
    if prefix:
        path.relative_to((root / prefix).resolve())
    return path


def git_info(root: Path) -> dict:
    commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    dirty = bool(subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=all"], cwd=root, text=True).strip())
    return {"git_commit": commit, "uncommitted_diff": dirty}


def parse_report(path: Path, task: str, machine: str) -> dict:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != f"# SUBSTEP REPORT — {task}":
        raise ValueError("Report task does not match")
    header = lines[1:next((i for i, line in enumerate(lines) if line.startswith("## ")), len(lines))]
    fields = dict(line.split(": ", 1) for line in header if ": " in line)
    if any(not fields.get(key) for key in REPORT_FIELDS):
        raise ValueError("Report has missing metadata")
    if fields["machine"] != machine or fields["status"] not in {"PASS", "FAIL", "BLOCKED"}:
        raise ValueError("Report machine/status does not match")
    for section in REPORT_SECTIONS:
        marker = f"## {section}"
        if marker not in lines:
            raise ValueError(f"Missing report section: {section}")
        start = lines.index(marker) + 1
        end = next((i for i in range(start, len(lines)) if lines[i].startswith("## ")), len(lines))
        if not any(line.strip() for line in lines[start:end]):
            raise ValueError(f"Empty report section: {section}")
    return fields
