# Fock-selected dark-sector viability

Operational contract: [AGENTS.md](AGENTS.md). Start each session with
[NEXT.md](NEXT.md) and [MACHINE_HANDOFF.md](MACHINE_HANDOFF.md), then read only
the referenced source/config/report. [STATUS.md](STATUS.md) is generated from
the canonical [state/state.yaml](state/state.yaml).

The repository begins at G0A-T01 on MACM6. Creating the repository establishes
engineering infrastructure; it is not evidence that any physics gate passes.

## Control commands

```sh
python3.12 -m venv .venv
.venv/bin/python scripts/ctl.py status
.venv/bin/python scripts/ctl.py queue --machine MACM6
.venv/bin/python scripts/ctl.py queue --machine RTX5070
.venv/bin/python scripts/ctl.py failures
.venv/bin/python scripts/ctl.py validate
.venv/bin/python scripts/ctl.py refresh
```

The publication `yayınlanan.pdf` is a required input for G0A-T02. Place the
exact published paper in the repository root and record its SHA256 before
deriving equations or numerical benchmarks. It is not bundled or fetched by
the setup task.

Run metadata and small logs are tracked. Large arrays/checkpoints and the
external publication are ignored. Their paths and SHA256 belong in reports.
The G0 task registry is initialized; later task entries are added from
AGENTS.md when their gates become active. Cloud and optional remote runners
are disabled. No remote Git repository is configured by this setup.
