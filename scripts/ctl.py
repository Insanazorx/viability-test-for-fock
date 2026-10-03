"""Canonical task state and generated views. No remote execution."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import re
import sys

from common import (MACHINES, ROOT, atomic_write, inside, parse_report, read_data,
                    sha256, write_data)

STATES = {"TODO", "CLAIMED", "RUNNING", "PASS", "FAIL", "BLOCKED", "ARCHIVED"}


def validate(state: dict) -> None:
    if state.get("schema_version") != 1 or not state.get("tasks"):
        raise ValueError("Missing state schema/tasks")
    tasks = state["tasks"]
    if state.get("active_task") is not None and state["active_task"] not in tasks:
        raise ValueError("Unknown focused task")
    for key, task in tasks.items():
        if not re.fullmatch(r"G[0-6][A-G]-T\d{2}", key):
            raise ValueError(f"Invalid task ID: {key}")
        order = task["machine_order"]
        if not order or len(order) != len(set(order)) or set(order) - set(MACHINES):
            raise ValueError(f"Invalid machine order: {key}")
        if task["status"] not in STATES:
            raise ValueError(f"Invalid state: {key}")
        done = task["machine_done"]
        if set(done) != set(MACHINES) or any(type(v) is not bool for v in done.values()):
            raise ValueError(f"Invalid completion flags: {key}")
        if any(done[m] for m in MACHINES if m not in order):
            raise ValueError(f"N/A machine marked done: {key}")
        if any(dep not in tasks or dep == key for dep in task["prerequisites"]):
            raise ValueError(f"Unknown/self prerequisite: {key}")
        overrides=task.get("machine_prerequisites", {})
        if overrides and not task.get("machine_prerequisite_reason", "").strip():
            raise ValueError(f"Machine prerequisites need a recorded reason: {key}")
        for machine, requirements in overrides.items():
            if machine not in order or not isinstance(requirements,list):
                raise ValueError(f"Invalid machine prerequisites: {key}")
            if len(requirements) != len(task['prerequisites']) or {r.get('task') for r in requirements} != set(task['prerequisites']):
                raise ValueError(f"Every task prerequisite must remain covered: {key}")
            for requirement in requirements:
                dependency=tasks[requirement['task']]
                if set(requirement)-{'task','machine'} or ('machine' in requirement and requirement['machine'] not in dependency['machine_order']):
                    raise ValueError(f"Invalid prerequisite responsibility: {key}")
        if any(done[m] and not done[previous] for i, m in enumerate(order)
               for previous in order[:i]):
            raise ValueError(f"Completion violates machine order: {key}")
        if task["status"] == "PASS" and not all(done[m] for m in order):
            raise ValueError(f"PASS without all required machines: {key}")
        if any(done[m] and not task["machine_reports"].get(m) for m in order):
            raise ValueError(f"Completion without report: {key}")
    visiting, visited = set(), set()

    def visit(key: str) -> None:
        if key in visiting:
            raise ValueError("Cyclic task prerequisites")
        if key in visited:
            return
        visiting.add(key)
        for dep in tasks[key]["prerequisites"]:
            visit(dep)
        visiting.remove(key)
        visited.add(key)

    for key in tasks:
        visit(key)
    cloud = state["cloud"]
    if type(cloud["paused"]) is not bool or cloud["max_usd_per_run"] < 0:
        raise ValueError("Invalid cloud guard")
    if not cloud["paused"] and (not cloud["approved_gate"] or cloud["max_usd_per_run"] <= 0):
        raise ValueError("Unpaused cloud requires gate and positive explicit budget")
    for machine, scheduling in state.get('machine_scheduling',{}).items():
        if machine not in MACHINES or type(scheduling.get('deferred')) is not bool or not scheduling.get('reason','').strip():
            raise ValueError('Invalid machine scheduling decision')


def ready(state: dict, task: dict, machine: str | None = None) -> bool:
    if not task['enabled'] or (machine and state.get('machine_scheduling',{}).get(machine,{}).get('deferred')):
        return False
    requirements=task.get('machine_prerequisites',{}).get(machine)
    if requirements is None:
        return all(state['tasks'][d]['status']=='PASS' for d in task['prerequisites'])
    for requirement in requirements:
        dependency=state['tasks'][requirement['task']]
        if 'machine' in requirement:
            responsibility=requirement['machine']
            if (dependency['status'] in {'FAIL','BLOCKED','ARCHIVED'} or not dependency['machine_done'][responsibility]
                    or not dependency['machine_reports'].get(responsibility)):
                return False
        elif dependency['status'] != 'PASS':
            return False
    return True


def pending_machine(task: dict) -> str | None:
    return next((m for m in task['machine_order'] if not task['machine_done'][m]),None)


def deferred_task(state: dict) -> tuple[str,dict] | None:
    """Expose the first ready deferred responsibility without scheduling it."""
    for key,task in state['tasks'].items():
        machine=pending_machine(task)
        if (task['status'] in {'TODO','CLAIMED','RUNNING'} and ready(state,task)
                and state.get('machine_scheduling',{}).get(machine,{}).get('deferred')):
            return key,task
    return None


def next_task(state: dict) -> tuple[str, dict] | None:
    focused = state.get("active_task")
    if focused:
        task = state["tasks"][focused]
        machine=pending_machine(task)
        if task["enabled"] and task["status"] not in {"PASS", "ARCHIVED"} and not state.get('machine_scheduling',{}).get(machine,{}).get('deferred'):
            return focused, task
    for key, task in state["tasks"].items():
        machine=pending_machine(task)
        if (task["enabled"] and task["status"] in {"CLAIMED", "RUNNING", "FAIL", "BLOCKED"}
                and not state.get('machine_scheduling',{}).get(machine,{}).get('deferred')):
            return key, task
    for key, task in state["tasks"].items():
        if task["status"] == "TODO" and ready(state, task, pending_machine(task)):
            return key, task
    return None


def flag(task: dict, machine: str) -> str:
    if machine not in task["machine_order"]:
        return "N/A"
    return "[X]" if task["machine_done"][machine] else "[ ]"


def render(state: dict, root: Path = ROOT) -> None:
    validate(state)
    current = next_task(state)
    waiting=deferred_task(state) if current is None else None
    action_label=current[0] if current else (f"none — {pending_machine(waiting[1])} deferred; next is {waiting[0]}" if waiting else 'none — review the task registry')
    summary = ["# STATUS", "", "Generated from state/state.yaml; do not edit by hand.", "",
               f"Active action: {action_label}",
               f"Cloud: {'PAUSED' if state['cloud']['paused'] else 'APPROVED'}; "
               f"budget USD {state['cloud']['max_usd_per_run']} per run.", "",
               "Only G0 tasks are registered initially. Later gates remain untested.", "",
               "| Task | Status | MACM6 | RTX5070 | CLOUD |",
               "|---|---|---|---|---|"]
    for key, task in state["tasks"].items():
        summary.append(f"| {key} | {task['status']}{' (disabled)' if not task['enabled'] else ''} | "
                       + " | ".join(flag(task, m) for m in MACHINES) + " |")
    cpu_freeze = state["environments"]["MACM6"].get("numerical_dependencies_frozen", False) if state.get("environments") else False
    summary.extend(["", "## Input/environment readiness", "",
                    "- Required publication: yayınlanan.pdf; availability is checked before G0A-T02.",
                    "- Python target: 3.12. MACM6 dependency freeze: " + ("complete." if cpu_freeze else "pending G0A-T03."),
                    "- Remote runner setup: disabled; no Git remote configured by bootstrap.", ""])
    program=state.get('macm6_program',{})
    if program.get('status')=='AVAILABLE_INPUT_WORK_COMPLETE':
        summary.extend(['','## MACM6 available-input program','',
                        '- Completed; GPU-derived postprocessing and missing physical-input calculations remain pending.',
                        '- Completion report: '+program['completion_report'],
                        '- Work summary: docs/MACM6_COMPLETION_SUMMARY.md'])
    for machine,scheduling in state.get('machine_scheduling',{}).items():
        if scheduling['deferred']:
            summary.append(f"- {machine}: DEFERRED — {scheduling['reason']}")
    atomic_write(root / "STATUS.md", "\n".join(summary))
    for machine in MACHINES:
        lines = [f"# {machine} CHECKLIST", "", "Generated from state/state.yaml.", ""]
        for key, task in state["tasks"].items():
            mark = flag(task, machine)
            lines.append(f"- {mark} {machine} — {key}: {task['title']} ({task['status']}"
                         + (", disabled" if not task["enabled"] else "") + ")")
        atomic_write(root / "docs" / f"{machine}_CHECKLIST.md", "\n".join(lines) + "\n")
    lines = ["# NEXT", "", "Exactly one active action; generated from state/state.yaml.", ""]
    if current:
        key, task = current
        machine = next((m for m in task["machine_order"] if not task["machine_done"][m]),
                       task["machine_order"][-1])
        lines.extend([f"task: {key}", f"machine: {machine}", f"status: {task['status']}", "",
                      "## Action", task.get("machine_actions", {}).get(machine, task["next_action"]), "", "## Read", "",
                      f"- AGENTS.md#{key[:3].lower()}", "- MACHINE_HANDOFF.md"])
        lines.extend(f"- {p}" for p in task["read"])
        lines.extend(["", "## One command", "", "```sh", task.get("machine_commands", {}).get(machine, task["command"]), "```", ""])
        if task["status"] in {"FAIL", "BLOCKED"}:
            lines.extend(["Resolve the recorded outcome before launching any new run.", ""])
    elif waiting:
        key,task=waiting;machine=pending_machine(task)
        lines.extend([f'task: {key}',f'machine: {machine}',f"status: {task['status']}",'scheduling: DEFERRED','',
                      '## Action','Preserve the completed MACM6 references and review the waiting handoff. '
                      'RTX5070 remains deferred at the user request; resume execution only on a new explicit user instruction.','',
                      '## Read','',f'- AGENTS.md#{key[:3].lower()}','- MACHINE_HANDOFF.md'])
        lines.extend(f'- {path}' for path in task['read'])
        lines.extend(['','## One command','','```sh','.venv/bin/python scripts/ctl.py status','```',''])
    else:
        lines.extend(["Review the task registry and add the next contract-defined task.", ""])
    atomic_write(root / "NEXT.md", "\n".join(lines))


def ensure_machine_ready(state: dict, key: str, machine: str) -> dict:
    task = state["tasks"][key]
    if not ready(state, task, machine):
        raise ValueError("Task disabled, machine deferred, or assigned prerequisites have not passed")
    if machine not in task["machine_order"]:
        raise ValueError("Machine is N/A for this task")
    if task["machine_done"][machine]:
        raise ValueError("This machine is already done")
    for previous in task["machine_order"][:task["machine_order"].index(machine)]:
        if not task["machine_done"][previous]:
            raise ValueError("Previous machine has not completed its responsibility")
    return task


def machine_done(state: dict, key: str, machine: str, report: str, root: Path = ROOT) -> None:
    task = ensure_machine_ready(state, key, machine)
    if task["status"] not in {"CLAIMED", "RUNNING"}:
        raise ValueError("Start the task before recording completion")
    path = inside(root, report, "reports")
    fields = parse_report(path, key, machine)
    run_id = fields["run_ids"]
    run = inside(root, f"runs/{run_id}", "runs")
    metadata, result = read_data(run / "metadata.json"), read_data(run / "result.json")
    if metadata.get("integrity_schema_version") or fields.get("evidence_sha256") or (run / "integrity.json").exists():
        from provenance import verify_run
        if fields.get("evidence_sha256") != verify_run(run):
            raise ValueError("Report does not match sealed run evidence")
    if (metadata["task"], metadata["machine"], result["status"]) != (key, machine, fields["status"]):
        raise ValueError("Run evidence does not match report")
    if metadata["config_sha256"] != fields["config_sha256"] or sha256(run / "config.yaml") != fields["config_sha256"]:
        raise ValueError("Frozen config hash does not match report")
    if metadata["git_commit"] != fields["git_commit"]:
        raise ValueError("Report commit does not match run")
    if result.get('checkpoint_sha256'):
        checkpoint=inside(root,result['checkpoint_path'],'checkpoints')
        if sha256(checkpoint)!=result['checkpoint_sha256']:
            raise ValueError('Referenced checkpoint hash changed')
    task["machine_done"][machine] = True
    task["machine_reports"][machine] = path.relative_to(root.resolve()).as_posix()
    if fields["status"] != "PASS":
        task["status"] = fields["status"]
    elif all(task["machine_done"][m] for m in task["machine_order"]):
        task["status"] = "PASS"
    else:
        task["status"] = "RUNNING"
    if state.get("active_task") == key and (task["status"] == "PASS" or
            (fields['status']=='PASS' and state.get('action_selection',{}).get('machine')==machine)):
        state["active_task"] = None


def focus(state: dict, key: str, machine: str, reason: str) -> None:
    """Select one independent next action without completing a waiting device."""
    ensure_machine_ready(state, key, machine)
    if state["tasks"][key]["status"] in {"PASS", "FAIL", "BLOCKED", "ARCHIVED"}:
        raise ValueError("Focused task requires an explicit recovery decision")
    if not reason.strip():
        raise ValueError("An action-selection reason is required")
    state["active_task"] = key
    state["action_selection"] = {"task": key, "machine": machine, "reason": reason,
                                 "selected_utc": datetime.now(timezone.utc).isoformat()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("status", "failures", "validate", "refresh", "pause-cloud"):
        commands.add_parser(name)
    queue = commands.add_parser("queue")
    queue.add_argument("--machine", choices=MACHINES, required=True)
    selection = commands.add_parser("focus")
    selection.add_argument("task")
    selection.add_argument("--machine", choices=MACHINES, required=True)
    selection.add_argument("--reason", required=True)
    for name in ('defer-machine','resume-machine'):
        scheduling=commands.add_parser(name)
        scheduling.add_argument('--machine',choices=MACHINES,required=True)
        scheduling.add_argument('--reason',required=True)
    for name in ("start", "machine-done"):
        command = commands.add_parser(name)
        command.add_argument("task")
        command.add_argument("--machine", choices=MACHINES, required=True)
        if name == "machine-done":
            command.add_argument("--report", required=True)
    args = parser.parse_args()
    state = read_data(ROOT / "state/state.yaml")
    validate(state)
    if args.command in {"start", "machine-done", "pause-cloud", "refresh", "focus",'defer-machine','resume-machine'}:
        if args.command == "start":
            task = ensure_machine_ready(state, args.task, args.machine)
            if task["status"] not in {"TODO", "CLAIMED", "RUNNING"}:
                raise ValueError("Failed/blocked/archived tasks need an explicit recovery decision")
            active = next_task(state)
            if active and active[0] != args.task and active[1]["status"] in {"CLAIMED", "RUNNING", "FAIL", "BLOCKED"}:
                raise ValueError("Resolve the current active action first")
            if task.get("required_input") and not inside(ROOT, task["required_input"]).is_file():
                raise ValueError(f"Required input is absent: {task['required_input']}")
            task["status"] = "CLAIMED"
            write_data(ROOT / "state/state.yaml", state)
            task["status"] = "RUNNING"
        elif args.command == "machine-done":
            machine_done(state, args.task, args.machine, args.report)
        elif args.command == "pause-cloud":
            state["cloud"]["paused"] = True
        elif args.command == "focus":
            focus(state, args.task, args.machine, args.reason)
        elif args.command in {'defer-machine','resume-machine'}:
            if not args.reason.strip():
                raise ValueError('Scheduling requires an explicit reason')
            state.setdefault('machine_scheduling',{})[args.machine]={
                'deferred':args.command=='defer-machine','reason':args.reason,
                'updated_utc':datetime.now(timezone.utc).isoformat()}
        state["updated_utc"] = datetime.now(timezone.utc).isoformat()
        validate(state)
        write_data(ROOT / "state/state.yaml", state)
        render(state)
    if args.command == "queue":
        for key, task in state["tasks"].items():
            if args.machine in task["machine_order"] and not task["machine_done"][args.machine] and task["enabled"]:
                try:
                    ensure_machine_ready(state, key, args.machine)
                    readiness = "ready" if task["status"] in {"TODO", "CLAIMED", "RUNNING"} else "requires recovery decision"
                except ValueError as error:
                    readiness = str(error)
                print(f"{key}: {task['status']} — {readiness}")
    elif args.command == "failures":
        failures = [(k, t) for k, t in state["tasks"].items() if t["status"] in {"FAIL", "BLOCKED"}]
        print("\n".join(f"{k}: {t['status']}" for k, t in failures) or "No recorded failures or blocked tasks.")
    elif args.command == "status":
        print((ROOT / "STATUS.md").read_text(encoding="utf-8"))
    else:
        print(f"{args.command}: OK")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError) as error:
        print(f"ctl: {error}", file=sys.stderr)
        raise SystemExit(1)
