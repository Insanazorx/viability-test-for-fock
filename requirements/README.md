# Environment policy

MACM6 uses Python 3.12 in its ignored `.venv`. JSON state/status commands use
the standard library; the acceptance launcher additionally uses the installed
config, memory and numerical dependencies below.

`macm6.txt` pins direct CPU dependencies. G0A-T03 resolves them in `.venv` and
freezes all distributions (including transitive dependencies and pip) in
`macm6.freeze.txt`, with its SHA256 in the report. That full freeze targets
MACM6 macOS arm64 on Python 3.12. `macm6-core.freeze.txt` preserves the earlier
NumPy-only math-core environment and must not be overwritten.

The control commands that only read JSON state remain standard-library based.
Full safe YAML, schema validation and memory profiling require PyYAML,
jsonschema and psutil; install the full freeze before acceptance runs.

RTX5070's CUDA/PyTorch build will be selected and frozen after checking its
actual driver and hardware. MPS is not an acceptance reference. No CUDA build,
cloud environment, CLASS installation, or inference framework is chosen here.
