"""Keep the full-program view complete without promoting plans to evidence."""
import copy
from pathlib import Path
import re
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from common import ROOT, read_data
from ctl import deferred_task, next_task, render
from status_dashboard import build_status, stage_status, task_flags, validate_roadmap


class StatusDashboardTests(unittest.TestCase):
    def setUp(self):
        self.state = read_data(ROOT / "state/state.yaml")

    def test_every_source_stage_and_numbered_task_is_present(self):
        source = (ROOT / "AGENTS.md").read_text()
        expected_stages = {f"G{number}{letter}" for number, letter in
                           re.findall(r"^## GATE ([0-6])-([A-G])", source, re.M)}
        expected_tasks = set(re.findall(r"^### (G[0-6][A-G]-T\d{2})\b", source, re.M))
        stages = self.state["roadmap"]["stages"]
        self.assertEqual({stage["id"] for stage in stages}, expected_stages)
        self.assertEqual({row["id"] for stage in stages for row in stage["tasks"]
                          if row["kind"] == "contract"}, expected_tasks)
        validate_roadmap(self.state)

    def test_scoped_pass_cannot_close_unnumbered_full_scope(self):
        stage = {"optional": False, "tasks": [
            {"id": "G4B", "kind": "full_scope"},
            {"id": "G4B-T01", "kind": "scoped"}]}
        state = {"tasks": {"G4B-T01": {"status": "PASS", "enabled": True}}}
        self.assertEqual(stage_status(stage, state), "PARTIAL")

    def test_preparation_pass_cannot_close_original_contract(self):
        stage = {"optional": False, "tasks": [
            {"id": "G1A-T01", "kind": "contract"},
            {"id": "G1A-T04", "kind": "preparation"}]}
        state = {"tasks": {"G1A-T01": {"status": "TODO", "enabled": True},
                           "G1A-T04": {"status": "PASS", "enabled": True}}}
        self.assertEqual(stage_status(stage, state), "PREPARED")
        state["tasks"]["G1A-T01"]["status"] = "PASS"
        self.assertEqual(stage_status(stage, state), "PASS")

    def test_plan_flags_wait_and_live_flags_use_actual_assignment(self):
        row = {"id": "G6C", "machine_order": ["CLOUD", "MACM6"]}
        self.assertEqual(task_flags(row, {"tasks": {}}), ["[ ]", "N/A", "[ ]"])
        row = {"id": "G0A-T02", "machine_order": ["CLOUD"]}
        state = {"tasks": {row["id"]: {
            "machine_order": ["MACM6", "RTX5070"],
            "machine_done": {"MACM6": True, "RTX5070": False, "CLOUD": False}}}}
        self.assertEqual(task_flags(row, state), ["[X]", "[ ]", "N/A"])

    def test_full_render_keeps_state_and_next_action_unchanged(self):
        before = copy.deepcopy(self.state)
        current = next_task(self.state)
        waiting = deferred_task(self.state) if current is None else None
        text = build_status(self.state, current, waiting, ROOT)
        for stage in self.state["roadmap"]["stages"]:
            self.assertIn(f'### {stage["id"]} — ', text)
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            render(self.state, root)
            self.assertEqual((root / "NEXT.md").read_text(), (ROOT / "NEXT.md").read_text())
            self.assertEqual((root / "NEXT.md").read_text().count("task: "), 1)
        self.assertEqual(self.state, before)
        self.assertEqual(next_task(self.state), current)
        self.assertEqual(deferred_task(self.state), deferred_task(before))

    def test_omitting_registered_evidence_from_catalog_is_rejected(self):
        value = copy.deepcopy(self.state)
        omitted = next(iter(value["tasks"]))
        for stage in value["roadmap"]["stages"]:
            stage["tasks"] = [row for row in stage["tasks"] if row["id"] != omitted]
        with self.assertRaisesRegex(ValueError, "Registered task omitted"):
            validate_roadmap(value)


if __name__ == "__main__":
    unittest.main()
