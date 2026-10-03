# Verified RTX5070 transfer packet

- Current packet: transfers/RTX5070__20261003T144940Z__9da2c46.zip
- SHA256: `b600fbb9cab9e2717754a320c4444e33aa662612de6e73137e45a46c3bc137b5`
- Size: 2412068 bytes
- Repository snapshot: `9da2c4641a8fa21394a2e7e1bbb29d571dfc7cb1`
- Isolated restore: PASS — 249 tracked files byte-identical, Git branch/commit, canonical state, all frozen config hashes, source PDF/checkpoint hashes, 14 MACM6 flags, unfinished RTX5070 flags and paused cloud verified on MACM6.

The packet includes the expanded G0–G6 STATUS and the later G0 scope clarification:
two RTX-independent CPU source benchmarks remain TODO plan scope. It contains
REPOSITORY.bundle, TRANSFER.json, BASLANGIC.md, the exact source PDF and the
independent nonstationary Hopf checkpoint. It excludes .venv and carries no
CUDA result or mid-iteration optimizer resume state. Actual Windows/Linux CUDA
setup and acceptance remain unverified until RTX5070 execution.

Copy this ZIP to RTX5070, extract it, open the extracted folder in Codex and
follow BASLANGIC.md. The restored permanent project is repo/. First real
RTX5070 task: G0A-T02. Read docs/DEVICE_CONTINUATION.md and docs/RTX5070_READY.md.

This receipt and its pointer in canonical state are recorded after the immutable
packet was produced; the packet carries the source commit above. On restoration,
TRANSFER.json is authoritative for payload identity; older packet pointers inside
the Git history are historical receipt metadata. All code/scientific task states,
configs, reports and source/checkpoint bytes were verified against that snapshot.
Earlier packets remain preserved. No remote execution, publication or cloud
activation was performed.
