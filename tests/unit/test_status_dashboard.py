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

    def test_remaining_overview_uses_live_tasks_without_promoting_plans(self):
        text = build_status(self.state, next_task(self.state), None, ROOT)
        overview = text.split('## Öncelikli kalan işler', 1)[1].split('## Cihazların durumu', 1)[0]
        for key, task in self.state['tasks'].items():
            expected = task['enabled'] and task['status'] not in {'PASS', 'ARCHIVED'}
            self.assertEqual(f'| {key} |' in overview, expected)
        self.assertIn('TODO · plan', overview)
        self.assertIn('G0D runner işleri kapalıdır', overview)

    def test_bundle_record_is_not_a_scientific_completion(self):
        value = copy.deepcopy(self.state)
        value['repository_history'] = {
            'status': 'VERIFIED', 'verified_utc': '2026-10-03T21:14:42Z',
            'audit_report': 'reports/G0/bundle.md', 'bundle_path': 'REPOSITORY.bundle',
            'bundle_bytes': 385317, 'bundle_sha256': 'a'*64,
            'restored_branch': 'codex/macm6-completion', 'tip': 'b'*40,
            'commit_count': 34, 'current_branch': 'reproduce/rtx5070-cuda',
            'macm6_reports_byte_identical': 14, 'original_evidence_files_byte_identical': 128,
            'frozen_configs_byte_identical': 24, 'historical_run_commits_available': 18,
            'remote': 'https://github.com/Insanazorx/viability-test-for-fock.git'}
        before = copy.deepcopy(value)
        text = build_status(value, next_task(value), None, ROOT)
        self.assertIn('**34 commit**', text)
        self.assertIn('dış manifest eşleşmesi iddia edilmez', text)
        self.assertNotIn('Git remote ve uzak runner kurulumu yok', text)
        self.assertIn('**PARTIAL / UNRESOLVED**', text)
        self.assertEqual(value, before)

    def test_g0_general_benchmarks_prevent_premature_main_gate_pass(self):
        value = copy.deepcopy(self.state)
        for key, task in value['tasks'].items():
            if key.startswith(('G0A', 'G0B', 'G0C')):
                task['status'] = 'PASS'
                for machine in task['machine_order']:
                    task['machine_done'][machine] = True
                    task['machine_reports'][machine] = 'reports/fixture.md'
        text = build_status(value, None, None, ROOT)
        row = next(line for line in text.splitlines() if line.startswith('| [G0](#g0)'))
        self.assertIn('**PARTIAL**', row)
        self.assertIn('Homojen tetikleme benchmark', text)
        value['dashboard']['g0_cpu_remaining'] = []
        text = build_status(value, None, None, ROOT)
        row = next(line for line in text.splitlines() if line.startswith('| [G0](#g0)'))
        self.assertIn('**PASS**', row)


if __name__ == "__main__":
    unittest.main()
