"""Create exactly one evidence-backed report for an infrastructure run."""
from __future__ import annotations

import argparse
import json
import sys

from common import ROOT, inside, read_data, sha256


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    run = inside(ROOT, f"runs/{args.run_id}", "runs")
    metadata, result = read_data(run / "metadata.json"), read_data(run / "result.json")
    if metadata["run_id"] != args.run_id or result["run_id"] != args.run_id:
        raise ValueError("Run ID does not match evidence")
    if metadata["task"] != "G0A-T01":
        raise ValueError("Automatic report prose is implemented only for G0A-T01")
    if sha256(run / "config.yaml") != metadata["config_sha256"]:
        raise ValueError("Config snapshot was changed")
    if result["status"] not in {"PASS", "FAIL", "BLOCKED"}:
        raise ValueError("Unsupported result status")
    metrics = result["metrics"]
    artifacts = []
    for name in ("config.yaml", "metadata.json", "result.json", "validation.log"):
        path = run / name
        if path.is_file():
            artifacts.append(f"- `{path.relative_to(ROOT).as_posix()}` — SHA256 `{sha256(path)}`")
    anomalies = [f"Dirty Git tree at run start: {metadata['uncommitted_diff']}.",
                 "Python 3.12.14 control environment exists; numerical dependencies are not yet installed/frozen.",
                 "No Git remote or remote runner is configured. CLOUD remains paused.",
                 "Hardware model/RAM capacity was not measured; MACM6 denotes the assigned control responsibility."]
    if not metrics.get("publication_present"):
        anomalies.append("`yayınlanan.pdf` is absent. This does not fail G0A-T01, but G0A-T02 cannot start without it.")
    if result.get("anomaly"):
        anomalies.append(result["anomaly"])
    values = {
        "task": metadata["task"], "machine": metadata["machine"], "status": result["status"],
        "git_commit": metadata["git_commit"], "config_sha256": metadata["config_sha256"],
        "run_id": args.run_id, "started_utc": metadata["started_utc"],
        "finished_utc": result["finished_utc"], "wall_time": f"{result['wall_time_seconds']:.6f} seconds",
        "peak_ram_gb": f"{result['peak_ram_gb']:.6f} ({result['peak_ram_method']})",
        "peak_vram_gb": "N/A — no GPU execution", "precision": metadata["precision"],
        "objective": "Complete G0A-T01: committed repository skeleton, canonical state, config schema and report template on MACM6.",
        "inputs": f"AGENTS.md §§3–7, G0A-T01 and §17; config `{metadata['config_path']}`. No publication contents are required for this setup substep.",
        "method": "Engineering validation only: Python standard-library control plane, complete path inventory, automated control-plane tests and Git provenance capture. No numerical physics calculation was performed.",
        "tolerances": "Every required path exists; state validation succeeds; all control tests exit successfully; CLOUD is paused. No physics tolerance is relaxed or evaluated.",
        "metrics": "```json\n" + json.dumps(metrics, indent=2, ensure_ascii=False) + "\n```",
        "convergence": "Not applicable to a repository setup. Regression checks cover machine-order enforcement, N/A rendering, dependency rejection, report/config evidence and generated views.",
        "evaluation": f"{result['status']} for G0A-T01 infrastructure only. Direct dependency pins and a Python 3.12 environment are present; full numerical dependency locking and run/seed discipline remain G0A-T03. No scientific gate has passed.",
        "anomalies": "\n".join(f"- {line}" for line in anomalies),
        "artifacts": "\n".join(artifacts) + "\nNo checkpoint or large numerical array was produced. Source/config code is identified by the Git commit above.",
        "reproduction": f"```sh\npython3.12 -m venv .venv\n.venv/bin/python -m unittest discover -s tests/unit -v\n.venv/bin/python scripts/ctl.py validate\n```\nFor an identified re-run, use an isolated checkout of `{metadata['git_commit']}` (where G0A-T01 is RUNNING), then `.venv/bin/python scripts/run.py --config {metadata['config_path']}`. A completed task is not silently reopened.",
        "changes": "First setup report; no previous report or physics implementation exists.",
        "next_action": "G0A-T02 on MACM6: restore/hash the exact `yayınlanan.pdf`, then derive Appendix A core definitions and their reference checks. Device switching waits for the committed mathematical core.",
        "handoff": "NEXT.md, MACHINE_HANDOFF.md, AGENTS.md#g0a; no transfer to RTX5070 or CLOUD yet.",
    }
    report = ROOT / "reports/G0" / f"G0A-T01__{args.run_id}__REPORT.md"
    with report.open("x", encoding="utf-8") as stream:
        stream.write((ROOT / "reports/SUBSTEP_REPORT_TEMPLATE.md").read_text(encoding="utf-8").format(**values))
    print(report.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError) as error:
        print(f"report: {error}", file=sys.stderr)
        raise SystemExit(1)
