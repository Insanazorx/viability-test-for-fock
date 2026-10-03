# Runbook

## Session entry

1. Read AGENTS.md, NEXT.md, MACHINE_HANDOFF.md, and only their referenced files.
2. Use the explicit machine name MACM6, RTX5070, or CLOUD.
3. Follow the one active action in NEXT.md. Preserve failed branches and reports.

## Python and file format

Use Python 3.12; `.venv` is machine-specific and ignored by Git. Recreate it
with `python3.12 -m venv .venv` on another machine. The current MACM6 environment
uses Python 3.12.14. The full CPU environment is frozen in
`requirements/macm6.freeze.txt`; the earlier NumPy-only math reference remains
in `requirements/macm6-core.freeze.txt`. Install the full freeze on another
MACM6 checkout; CUDA/other operating systems require their own environment.

State/schema files are JSON-formatted YAML 1.2. Run configs also support safe
YAML, with duplicate keys, non-finite values and unsafe constructors rejected.
Schema validation uses Draft 2020-12 and a predeclared handler registry. Any
byte change in a registered config, including whitespace, requires an explicit
review/freeze and commit before acceptance runs:

```sh
.venv/bin/python scripts/configuration.py freeze
.venv/bin/python scripts/configuration.py check
```

Freeze does not launch a job or change a machine completion flag. The config
hash registry is tracked; historical run snapshots/reports are preserved.

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

## Full-program status

`state/state.yaml` contains two separate records: `tasks` is the executable
task registry with report-bound device flags; `roadmap` is the full G0–G6
display catalog derived from AGENTS.md. A roadmap-only TODO row is a plan,
not a scheduled or registered task. Stages without source task IDs retain
their stage ID as a full-scope display row.

```sh
.venv/bin/python scripts/ctl.py refresh
.venv/bin/python scripts/ctl.py validate
```

STATUS.md includes every stage, acceptance criteria, dependencies, machine
responsibilities, report links, scoped results and missing inputs. Its
`dashboard` metadata holds report-backed summary measurements. Preserve
`preparation` and `scoped` row classifications: a PASS for those rows does
not close the original full scientific stage. When new work is registered,
update the display catalog too; validation rejects omitted registered tasks.
Refreshing this view does not add tasks, change completion flags or enable
deferred devices/cloud. NEXT remains exactly one executable or waiting action.

When a device is unavailable, a dependency-ready independent task can become
the single active NEXT action with an explicit recorded reason:

```sh
.venv/bin/python scripts/ctl.py focus G0A-T03 --machine MACM6 --reason 'RTX5070 unavailable; user requests independent MACM6 infrastructure'
```

This changes only action selection, never a prerequisite outcome or another
machine's flag. Completing that task returns NEXT to the waiting device task.

## Setup validation and report

```sh
.venv/bin/python scripts/run.py --config config/benchmark/g0a_t01.json.yaml
.venv/bin/python scripts/report.py --run-id EXACT_RUN_ID
```

Installed handlers cover repository/config discipline, MACM6/CUDA core/spectral/Hopf references, MACM6 solver/full-M preparation, G4 symmetry/dark-loop/conditional-status/bounce preparation and offline transfer preflight. The matched stationary sequence and physical eigenspectrum production drivers remain RTX5070 development work. Runs capture source/
config hashes, full installed versions, dirty Git state, UTC identity, explicit
seeds/precision and measured hardware. Numerical handlers use their declared
per-seed generators; Python/NumPy global seeds are also initialized explicitly.
CUDA acceptance uses explicit FP64, seeded Torch, deterministic algorithms and
disabled TF32, with actual runtime/device/driver information where available.
These CUDA policies are implemented but remain unverified until RTX5070 runs.

Run snapshots are exclusive/read-only; an integrity manifest hashes config,
metadata, environment, result and validation log. The report binds that seal's
hash and completion verifies it. Same-second identity collisions reject an
overwrite. Parent/registered-child RAM is sampled at 10 ms; this is an observed
peak, not a guarantee that brief transients are captured. Windows portability
has been implemented but not executed. No host-wide process enumeration occurs.

A read-only config/device preflight creates no run or result:

```sh
.venv/bin/python scripts/run.py --check --config config/benchmark/g0a_t02_rtx5070.json.yaml
```

After any completed or failed run: create its report, record the machine
completion with `ctl.py`, update the short handoff, and commit code/config,
small metadata and reports. Push only when a remote has been configured.

## Cloud

Cloud starts paused, with no approved gate and zero budget. This skeleton has
no cloud provisioner or remote executor. Cloud/remote execution requires the
explicit prerequisites and approval packet specified in AGENTS.md.
# CPU preparation while a machine is deferred

When the user explicitly defers a machine, record that scheduling decision:

```sh
.venv/bin/python scripts/ctl.py defer-machine --machine RTX5070 --reason 'User requested RTX5070 later'
```

The machine completion flags remain unchanged. Ready MACM6 preparation may
use explicitly recorded `machine_prerequisites` only when every parent
prerequisite is covered and the completed responsibility has a report.
G0B-T01 MACM6 uses G0A-T02 MACM6 and whole G0A-T03; its RTX5070 responsibility
still requires the whole parent tasks. See `docs/G0B_SPECTRAL.md`.

Resume a deferred machine only on a later user instruction:

```sh
.venv/bin/python scripts/ctl.py resume-machine --machine RTX5070 --reason 'User requested RTX5070 continuation'
```

This returns RTX5070 to its earliest unfinished work, G0A-T02 CUDA. It does
not imply cloud approval or install a remote runner.
