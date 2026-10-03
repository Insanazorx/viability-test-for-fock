# RTX5070 — prepared MACM6 handoff

## Verified device continuation: 2026-10-03

RTX5070 is now resumed by explicit user instruction. The actual Windows 11
Home / Python 3.12.14 environment is recorded in `docs/RTX5070_ENVIRONMENT.json`
and frozen in `requirements/rtx5070.freeze.txt`. PyTorch 2.11.0+cu128 executes
float64 tensors/FFT on NVIDIA GeForce RTX 5070 (sm_120), driver 616.92.
Both external input hashes match. The checkpoint remains nonstationary.

GitHub remote: `https://github.com/Insanazorx/viability-test-for-fock.git`.
Working branch: `reproduce/rtx5070-cuda`. The downloaded directory had no
`.git`; metadata was restored from this remote without replacing source files.
The remote begins with a single upload commit, not the original MACM6 history.
Original MACM6 reports and artifact bytes are preserved. The original Git
bundle is still needed to recover those earlier commit objects.

This device uses `.venv/Scripts/python.exe`. If Git is absent from the shell,
add `.venv/tools/mingit/cmd` to that shell's PATH. Portable Git and GitHub CLI
are installed only in this ignored environment. Frozen configs and run/report
evidence retain exact bytes through `.gitattributes`. Source PDF, HDF5 files,
the environment and generated Python caches are excluded from new commits.

Follow generated `NEXT.md`. CLOUD remains paused with budget USD 0; optional
remote runners remain disabled. CUDA backend acceptance does not close the
stationary solver/Hessian or full scientific viability gates.

## Original MACM6 transfer instructions

MACM6 available-input preparation is complete after the transfer preflight report. The repository has no Git remote; the offline ZIP contains a full-history Git bundle, the exact source PDF and the independent Hopf fixture checkpoint. Its SHA256 is recorded beside the delivered package. It contains no MACM6 environment or GPU completion claim.

Extract the ZIP into a staging folder. Clone REPOSITORY.bundle (branch codex/macm6-completion) into the desired project directory, then copy yayınlanan.pdf and the checkpoints folder from staging into that checkout. All tracked code/configs/reports/state arrive through the bundle; do not initialize a separate blank repository. Read AGENTS.md, NEXT.md and MACHINE_HANDOFF.md in the restored checkout. TRANSFER.json lists each payload hash and the exact commit.

Create a Python3.12 environment on RTX5070. Install direct tool/CPU dependencies from requirements/macm6.txt and a CUDA-enabled PyTorch build chosen for the actual OS/driver/GPU. The MACM6 macOS freeze is not a Windows/Linux CUDA lock. Record/freeze actual versions before acceptance. No particular driver/build compatibility has been attested by MACM6.

The first real device task is **G0A-T02**, then **G0B-T01**, then **G0B-T02**. These three frozen CUDA configs and actual CUDA/NumPy/autograd comparisons are implemented. G0B-T03 reduced minimizer and G0B-T04 HVP ingredients are prepared, but their GPU acceptance driver, matched source stationary sequence, collective catalog/eigensolver and physical spectrum must still be completed on RTX5070. They are not executable production gate claims merely because code ingredients exist.

When the user opens this project on RTX5070 and requests continuation, use that machine's Python executable (`.venv/bin/python` on Linux, `.venv\Scripts\python.exe` on Windows) to resume the deferred machine, focus G0A-T02 and run its read-only device preflight:

```sh
PYTHON scripts/ctl.py resume-machine --machine RTX5070 --reason 'User opened the prepared project on RTX5070 and requested continuation'
PYTHON scripts/ctl.py focus G0A-T02 --machine RTX5070 --reason 'First CUDA mirror after MACM6 preparation'
PYTHON scripts/run.py --check --config config/benchmark/g0a_t02_rtx5070.json.yaml
```

Replace PYTHON with the machine's actual environment executable. A real CUDA float64 tensor/device must be visible; CPU/MPS is not accepted. Then follow NEXT's one command, create the report and record only RTX5070 completion. Use the report from this run; never mark CUDA done from the MACM6 report.

G0B-T03 keeps the predeclared17^3,21^3,25^3,33^3 sequence, fixed published grid/box, residual, energy/charge tolerances and separate equivalence-report requirement. The compact initializer in the packet is independently derived and nonstationary. If the archived production initializer remains absent, document its influence on reproducibility and solver equivalence rather than silently relaxing source targets.

G1 branch persistence/collisions, production data, astrophysical conversion, full radiative matching, gravitational lifetime, CLASS and likelihood gates remain dependent on their missing inputs/precursors. Cloud is paused with zero budget. Optional remote runners remain disabled until G0B passes.
