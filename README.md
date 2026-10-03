# Fock-selected dark-sector viability

Operational contract: [AGENTS.md](AGENTS.md). Start each session with
[NEXT.md](NEXT.md) and [MACHINE_HANDOFF.md](MACHINE_HANDOFF.md), then read only
the referenced source/config/report. [STATUS.md](STATUS.md) is generated from
the canonical [state/state.yaml](state/state.yaml).

G0A-T01 established the repository infrastructure. G0A-T02 adds the paper's
mathematical definitions and MACM6 float64 reference; its CUDA comparison is
assigned to RTX5070. Follow the current NEXT.md for the active responsibility.

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

The supplied publication `yayınlanan.pdf` is verified and its SHA256 is recorded
in `config/benchmark/publication.source.yaml`. It remains an external ignored
input; copy that exact file to the next machine. Mathematical conventions are
documented in `docs/MATH_CORE.md`; RTX5070 steps are in `docs/RTX5070_CORE_HANDOFF.md`.

Run metadata and small logs are tracked. Large arrays/checkpoints and the
external publication are ignored. Their paths and SHA256 belong in reports.
The G0 task registry is initialized; later task entries are added from
AGENTS.md when their gates become active. Cloud and optional remote runners
are disabled. No remote Git repository is configured by this setup.
