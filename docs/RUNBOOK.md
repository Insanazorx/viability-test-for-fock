# Runbook

## Session entry

1. Read AGENTS.md, NEXT.md, MACHINE_HANDOFF.md, and only their referenced files.
2. Use the explicit machine name MACM6, RTX5070, or CLOUD.
3. Follow the one active action in NEXT.md. Preserve failed branches and reports.

## Python and file format

Use Python 3.12; `.venv` is machine-specific and ignored by Git. Recreate it
with `python3.12 -m venv .venv` on another machine. The current MACM6 environment
uses the bundled Python 3.12.14 runtime. Numerical libraries are not installed.

State, schema and setup config are JSON-formatted YAML 1.2. This documented
subset allows the control plane to run without third-party libraries.
Preserve this format when editing them. The numerical config parser may gain
full safe YAML support under G0A-T03; that task remains uncompleted here.

## Task lifecycle

```sh
.venv/bin/python scripts/ctl.py start G0A-T02 --machine MACM6
.venv/bin/python scripts/ctl.py machine-done G0A-T02 --machine MACM6 --report reports/G0/EXACT_REPORT.md
```

`start` validates prerequisites and machine order, then moves TODO through
CLAIMED to RUNNING. `machine-done` checks the report's task, machine, status,
mandatory fields/sections and run evidence. It changes only the named
machine's flag, attaches the report, regenerates the dashboard/checklists,
and chooses exactly one next action. The report must describe its own
machine's responsibility. A PASS report completes a task only when all
required machines are done. FAIL/BLOCKED reports retain that outcome and
require an explicit diagnostic/recovery action; no automatic scan expansion.

`refresh` regenerates files without changing scientific outcomes. Do not edit
STATUS.md or device checklist files by hand. N/A means a machine is not required.
Optional G0D tasks are disabled until G0B passes and remote setup is requested.

## Setup validation and report

```sh
.venv/bin/python scripts/run.py --config config/benchmark/g0a_t01.json.yaml
.venv/bin/python scripts/report.py --run-id EXACT_RUN_ID
```

The only installed handler is the G0A-T01 infrastructure validator. It runs
control-plane tests and checks the required layout; it does not implement a
physics solver. Metadata/config snapshots are created exclusively and made
read-only; a reused run ID is rejected. A numerical launcher, CUDA/seed policy,
runtime profiling and resolved dependency freezes still belong to G0A-T03.

After any completed or failed run: create its report, record the machine
completion with `ctl.py`, update the short handoff, and commit code/config,
small metadata and reports. Push only when a remote has been configured.

## Cloud

Cloud starts paused, with no approved gate and zero budget. This skeleton has
no cloud provisioner or remote executor. Cloud/remote execution requires the
explicit prerequisites and approval packet specified in AGENTS.md.
