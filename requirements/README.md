# Environment policy

The control plane uses Python 3.12 and the standard library only. The initial
MACM6 environment is `.venv`; it does not yet contain numerical dependencies.

`macm6.txt` pins the direct CPU dependencies. Before a numerical run, G0A-T03
must install them in a dedicated environment, capture all resolved versions
in a platform-specific freeze file, and attach that file's SHA256 to the report.
Do not claim a fully resolved lock from this direct-dependency list.

RTX5070's CUDA/PyTorch build will be selected and frozen after checking its
actual driver and hardware. MPS is not an acceptance reference. No CUDA build,
cloud environment, CLASS installation, or inference framework is chosen here.
