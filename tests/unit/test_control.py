"""Contract regressions for bookkeeping that determines later scientific gates."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from common import (MACHINES, REPORT_FIELDS, REPORT_SECTIONS, ROOT, git_info,
                    inside, parse_report, read_data, sha256, write_data)
from ctl import ensure_machine_ready, flag, machine_done, next_task, record_failure, render, validate
from run import freeze


def task(order=("MACM6",), prerequisites=(), status="RUNNING"):
    return {"title": "Test responsibility", "status": status, "enabled": True,
            "machine_order": list(order), "machine_done": {m: False for m in MACHINES},
            "machine_reports": {}, "prerequisites": list(prerequisites),
            "next_action": "Perform one test action.", "read": [], "command": "python scripts/ctl.py validate"}


def state():
    return {"schema_version": 1, "cloud": {"paused": True, "approved_gate": None, "max_usd_per_run": 0},
            "tasks": {"G0A-T01": task(), "G0A-T02": task(("MACM6", "RTX5070"), ("G0A-T01",), "TODO")}}


def report_text(key="G0A-T01", machine="MACM6", status="PASS", digest="a" * 64):
    fields = {k: "fixture" for k in REPORT_FIELDS}
    fields.update(status=status, machine=machine, run_ids="fixture", config_sha256=digest)
    return (f"# SUBSTEP REPORT — {key}\n\n" + "\n".join(f"{k}: {v}" for k, v in fields.items())
            + "\n\n" + "\n".join(f"## {s}\nEvidence.\n" for s in REPORT_SECTIONS))


class ControlTests(unittest.TestCase):
    def test_control_json_keeps_lf_bytes_across_devices(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "state.yaml"
            write_data(path, {"machine": "RTX5070"})
            self.assertNotIn(b"\r", path.read_bytes())
            self.assertEqual(path.read_bytes(), b'{\n  "machine": "RTX5070"\n}\n')

    def test_canonical_state_is_valid(self):
        validate(read_data(ROOT / "state/state.yaml"))

    def test_na_is_never_completed(self):
        value = state()
        self.assertEqual(flag(value["tasks"]["G0A-T01"], "CLOUD"), "N/A")
        value["tasks"]["G0A-T01"]["machine_done"]["CLOUD"] = True
        with self.assertRaises(ValueError):
            validate(value)

    def test_cannot_pass_missing_machine(self):
        value = state()
        value["tasks"]["G0A-T01"]["status"] = "PASS"
        with self.assertRaises(ValueError):
            validate(value)

    def test_cannot_skip_dependencies(self):
        with self.assertRaises(ValueError):
            ensure_machine_ready(state(), "G0A-T02", "MACM6")

    def test_cannot_skip_machine_order(self):
        value = state()
        first = value["tasks"]["G0A-T01"]
        first.update(status="PASS", machine_reports={"MACM6": "report.md"})
        first["machine_done"]["MACM6"] = True
        with self.assertRaises(ValueError):
            ensure_machine_ready(value, "G0A-T02", "RTX5070")

    def test_dependency_cycles_rejected(self):
        value = state()
        value["tasks"]["G0A-T01"]["prerequisites"] = ["G0A-T02"]
        with self.assertRaises(ValueError):
            validate(value)

    def test_cloud_requires_approval_and_budget(self):
        value = state()
        value["cloud"]["paused"] = False
        with self.assertRaises(ValueError):
            validate(value)

    def test_failure_precedes_new_work(self):
        value = state()
        value["tasks"]["G0A-T01"]["status"] = "FAIL"
        self.assertEqual(next_task(value)[0], "G0A-T01")

    def test_disabled_tasks_not_selected(self):
        value = state()
        value["tasks"]["G0A-T01"]["enabled"] = False
        self.assertIsNone(next_task(value))

    def test_generated_views_show_one_action_and_na(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            render(state(), root)
            first = (root / "NEXT.md").read_text()
            render(state(), root)
            self.assertEqual(first, (root / "NEXT.md").read_text())
            self.assertEqual(first.count("task: "), 1)
            self.assertIn("N/A CLOUD", (root / "docs/CLOUD_CHECKLIST.md").read_text())

    def test_external_and_symlink_paths_rejected(self):
        with tempfile.TemporaryDirectory() as folder, tempfile.TemporaryDirectory() as outside:
            root = Path(folder)
            try:
                (root / "link").symlink_to(outside, target_is_directory=True)
            except OSError as error:
                if sys.platform != "win32" or error.winerror != 1314:
                    raise
                # Junctions test the same resolved-path escape without symlink privileges.
                subprocess.run(["powershell.exe", "-NoProfile", "-Command",
                                "New-Item -ItemType Junction -Path $env:FOCK_TEST_JUNCTION "
                                "-Target $env:FOCK_TEST_TARGET -ErrorAction Stop | Out-Null"],
                               env=dict(os.environ, FOCK_TEST_JUNCTION=str(root / "link"),
                                        FOCK_TEST_TARGET=outside), check=True)
            for name in ("../report.md", "link/report.md"):
                with self.assertRaises(ValueError):
                    inside(root, name)

    def test_next_uses_assigned_machine_python(self):
        value = state()
        value["tasks"]["G0A-T01"] = task(("RTX5070",))
        value["tasks"]["G0A-T01"]["command"] = ".venv/bin/python scripts/ctl.py validate"
        value["environments"] = {"RTX5070": {"python_command": ".venv/Scripts/python.exe"}}
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            render(value, root)
            self.assertIn(".venv/Scripts/python.exe scripts/ctl.py validate",
                          (root / "NEXT.md").read_text())

    def test_wrong_task_and_empty_report_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "report.md"
            path.write_text(report_text())
            with self.assertRaises(ValueError):
                parse_report(path, "G0A-T02", "MACM6")
            path.write_text(report_text().replace("## Objective\nEvidence.", "## Objective\n"))
            with self.assertRaises(ValueError):
                parse_report(path, "G0A-T01", "MACM6")

    def test_metadata_snapshot_cannot_be_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "metadata.json"
            freeze(path, {"config_sha256": "original"})
            with self.assertRaises(FileExistsError):
                freeze(path, {"config_sha256": "modified"})
            self.assertEqual(read_data(path)["config_sha256"], "original")
            self.assertEqual(path.stat().st_mode & 0o222, 0)

    def evidence(self, root, result_status="PASS"):
        run = root / "runs/fixture"
        run.mkdir(parents=True)
        (run / "config.yaml").write_text('{"version":1}\n')
        digest = sha256(run / "config.yaml")
        write_data(run / "metadata.json", {"task": "G0A-T01", "machine": "MACM6",
                   "config_sha256": digest, "git_commit": "fixture"})
        write_data(run / "result.json", {"status": result_status})
        report = root / "reports/G0/test.md"
        report.parent.mkdir(parents=True)
        report.write_text(report_text(digest=digest))
        return run, report

    def test_machine_done_only_changes_its_flag_and_advances_next(self):
        with tempfile.TemporaryDirectory() as folder:
            root, value = Path(folder), state()
            self.evidence(root)
            machine_done(value, "G0A-T01", "MACM6", "reports/G0/test.md", root)
            self.assertEqual(value["tasks"]["G0A-T01"]["machine_done"],
                             {"MACM6": True, "RTX5070": False, "CLOUD": False})
            self.assertEqual(value["tasks"]["G0A-T01"]["status"], "PASS")
            self.assertEqual(next_task(value)[0], "G0A-T02")
            with self.assertRaises(ValueError):
                machine_done(value, "G0A-T01", "MACM6", "reports/G0/test.md", root)

    def test_changed_config_cannot_mark_done(self):
        with tempfile.TemporaryDirectory() as folder:
            root, value = Path(folder), state()
            run, _ = self.evidence(root)
            (run / "config.yaml").write_text('{"version":2}\n')
            before = copy.deepcopy(value)
            with self.assertRaises(ValueError):
                machine_done(value, "G0A-T01", "MACM6", "reports/G0/test.md", root)
            self.assertEqual(value, before)

    def test_missing_report_does_not_change_state(self):
        with tempfile.TemporaryDirectory() as folder:
            root, value = Path(folder), state()
            before = copy.deepcopy(value)
            with self.assertRaises(FileNotFoundError):
                machine_done(value, "G0A-T01", "MACM6", "reports/G0/missing.md", root)
            self.assertEqual(value, before)

    def test_failure_evidence_cannot_be_declared_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            root, value = Path(folder), state()
            self.evidence(root, "FAIL")
            with self.assertRaises(ValueError):
                machine_done(value, "G0A-T01", "MACM6", "reports/G0/test.md", root)

    def test_git_dirty_provenance(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True)
            (root / "fixture.txt").write_text("original\n")
            subprocess.run(["git", "add", "fixture.txt"], cwd=root, check=True)
            subprocess.run(["git", "-c", "user.name=Control test", "-c", "user.email=control-test@localhost",
                            "commit", "-qm", "fixture"], cwd=root, check=True)
            self.assertFalse(git_info(root)["uncommitted_diff"])
            (root / "fixture.txt").write_text("changed\n")
            self.assertTrue(git_info(root)["uncommitted_diff"])
            self.assertEqual(len(git_info(root)["git_commit"]), 40)

    def test_failed_evidence_does_not_mark_machine_complete(self):
        with tempfile.TemporaryDirectory() as folder:
            root,value=Path(folder),state()
            run,report=self.evidence(root,'FAIL')
            report.write_text(report_text(status='FAIL',digest=sha256(run/'config.yaml')))
            before=copy.deepcopy(value['tasks']['G0A-T01']['machine_done'])
            record_failure(value,'G0A-T01','MACM6','reports/G0/test.md','optimizer',root)
            self.assertEqual(value['tasks']['G0A-T01']['machine_done'],before)
            self.assertEqual(value['tasks']['G0A-T01']['status'],'FAIL')
            self.assertEqual(value['tasks']['G0A-T01']['last_outcome']['classification'],'optimizer')
            self.assertEqual(next_task(value)[0],'G0A-T01')

    def test_failed_record_cannot_hide_pass_or_broken_checkpoint(self):
        with tempfile.TemporaryDirectory() as folder:
            root,value=Path(folder),state()
            run,report=self.evidence(root)
            with self.assertRaises(ValueError):
                record_failure(value,'G0A-T01','MACM6','reports/G0/test.md','unknown',root)
            checkpoint=root/'checkpoints/test.h5';checkpoint.parent.mkdir();checkpoint.write_bytes(b'state')
            write_data(run/'result.json',{'status':'FAIL','checkpoint_artifacts':[
                {'path':'checkpoints/test.h5','sha256':'0'*64}]})
            report.write_text(report_text(status='FAIL',digest=sha256(run/'config.yaml')))
            before=copy.deepcopy(value)
            with self.assertRaisesRegex(ValueError,'checkpoint hash changed'):
                record_failure(value,'G0A-T01','MACM6','reports/G0/test.md','unknown',root)
            self.assertEqual(value,before)


if __name__ == "__main__":
    unittest.main()
