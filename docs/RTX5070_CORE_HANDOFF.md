# RTX5070 G0A-T02 handoff

Read AGENTS.md#g0a, NEXT.md, MACHINE_HANDOFF.md, the MACM6 core report linked
there, `docs/MATH_CORE.md`, and `config/benchmark/g0a_t02_rtx5070.json.yaml`.

## Inputs and environment

Use the committed mathematical core on Python 3.12. Copy the external ignored
`yayınlanan.pdf` to this checkout. Its required SHA256 is
`09111940dc2575283d8db69ee65785d2b85beb3864e416e63c7538e91c70c312`.
The launcher rejects any different source identity.

Create this machine's `.venv`, install the direct CPU/tool dependencies from
`requirements/macm6.txt` and select a CUDA-enabled
PyTorch build compatible with the actual RTX5070 driver/device. Do not guess
or substitute MPS/CPU. Record the selected build and driver in its report;
the launcher also saves installed package versions, actual CUDA runtime/device,
and peak allocated VRAM. No PyTorch build was installed or verified on MACM6.

## One validation run

```sh
.venv/bin/python scripts/run.py --config config/benchmark/g0a_t02_rtx5070.json.yaml
```

The task is already RUNNING after MACM6 completion. The launcher enforces that
MACM6 finished first. It uses actual CUDA float64, three fixed seeds and 512
samples per seed, comparing the API with NumPy and independently differentiated
contractions. It exercises the nine contract definitions; CUDA arrays must
retain their device/dtype. No 3-D production, soliton solve, or cloud job occurs.

After the run, generate exactly one report and record only RTX5070 completion:

```sh
.venv/bin/python scripts/report.py --run-id EXACT_RUN_ID
.venv/bin/python scripts/ctl.py machine-done G0A-T02 --machine RTX5070 --report reports/G0/EXACT_REPORT.md
```

Verify PASS/FAIL before committing the report and the generated state files.
A negative/uncertain result does not become PASS. G0A-T03 is independent of
the CUDA mirror and can pass on MACM6 while this device is unavailable. Follow
NEXT.md after both G0A-T02 responsibilities pass. Cloud stays paused.
