# SUBSTEP REPORT - REPOSITORY_BUNDLE

status: PASS
machine: RTX5070
git_commit: ab208635d3b01b164c5c68f43a02ee915efc0403
config_sha256: N/A - repository control-plane audit, no numerical config
run_ids: N/A - no numerical run or new contract task
started_utc: not separately measured
finished_utc: 2026-10-03T21:14:42.864434+00:00
wall_time: not separately measured
peak_ram_gb: not measured
peak_vram_gb: N/A - no GPU execution
precision: N/A - exact-byte Git/hash comparisons

## Objective
Verify the user-supplied REPOSITORY.bundle, recover MACM6 provenance without
overwriting RTX5070 work, and regenerate STATUS from canonical state.
PASS here is an engineering audit, not a scientific gate or device completion.

## Inputs
- REPOSITORY.bundle: 385317 bytes; measured SHA256
  `b2b03fa07c1e8e9177316eee035af3831252829ef88e2b01438f53c87c888d3e`.
- docs/RTX5070_TRANSFER_PACKET.md records source snapshot
  `9da2c4641a8fa21394a2e7e1bbb29d571dfc7cb1`.
- state/state.yaml, NEXT.md, MACHINE_HANDOFF.md, RTX5070 readiness note,
  latest G0B-T02 CUDA and G0B-T05 MACM6 preparation reports.
- TRANSFER.json and the transfer ZIP are not present in this checkout.

## Numerical method
No numerical physics was executed. Git bundle verification, advertised-ref
inspection, fetch to a separate branch, object integrity checks, exact-byte
comparisons against the recovered tree, SHA256 of external inputs, and
canonical dashboard regeneration were used.

## Tolerances
Exact equality for commit identities and preserved evidence/config bytes.
No published energy/charge or numerical acceptance tolerance was changed.

## Primary metrics
- `git bundle verify`: PASS; complete history, SHA1 Git object format.
- Advertised refs: HEAD and refs/heads/codex/macm6-completion, both at the
  recorded source snapshot. Tip matches the MACM6 transfer receipt.
- Recovered history: 34 commits on codex/macm6-completion.
- All 14 current MACM6 completion reports byte-identical to the bundle tree.
- All 128 historical report/run evidence files byte-identical, including
  failed attempts; all 24 non-placeholder config files byte-identical.
- 18 historical run metadata records cite 18 distinct commits; all recovered
  and all ancestors of the bundle tip.
- All MACM6 completion flags and CLOUD guard match the bundle state.
- RTX5070 branch/HEAD and its passing/failing evidence preserved.
- Canonical registered tasks remain 14 PASS / 7 TODO. Only three RTX5070
  responsibilities are complete; no new task or machine flag was marked.
- Dashboard regression suite: 9 tests PASS. Full unit suite: 128 tests PASS
  in 25.773 seconds. These are implementation tests, not new physics runs.
- Canonical validation/refresh and full-reference Git fsck: PASS.
- All four existing RTX5070 run seals verify, including the preserved failed
  Hopf attempt. Task records, machine flags, prior reports, environment records,
  CLOUD and NEXT are unchanged from the pre-audit RTX5070 HEAD.

## Convergence checks
N/A for physics. Evidence was compared directly with original Git blobs;
commit presence and ancestry were independently checked.

## Pass/fail evaluation
PASS for Git integrity, source-tip identity and preservation checks. The
bundle's SHA256 is measured here, not matched to an independent payload
manifest: no TRANSFER.json or pre-recorded standalone bundle digest was
provided. The ZIP digest in the transfer receipt is not a bundle digest.

## Anomalies
- Current GitHub upload and recovered MACM6 history have separate roots.
  They remain on separate branches; no force-push, reset or merge performed.
- Four reports/runs .gitkeep placeholders and two config .gitkeep placeholders
  are absent in this downloaded tree. No evidence/config content is missing
  or changed; placeholders are excluded from the byte-identical counts.
- A tip-only fsck lists the separate RTX5070 commit as dangling relative to
  that selected tip, not corrupt. An unused tree object is harmless.
- Bundle includes only checkpoints/.gitkeep, not scientific checkpoint data.
  The paper's archived production initializer is still absent. Both available
  Hopf checkpoints are independent nonstationary fixtures.
- No CUDA run, minimization, Hessian spectrum or scientific gate closure was
  performed by this audit. CLOUD remains paused with zero budget.

## Artifacts/checkpoints
- Recovered Git branch: codex/macm6-completion.
- Working branch: reproduce/rtx5070-cuda.
- REPOSITORY.bundle remains on disk and is ignored by Git; identity above.
- Source PDF: yayınlanan.pdf, SHA256
  `09111940dc2575283d8db69ee65785d2b85beb3864e416e63c7538e91c70c312`.
- Original nonstationary checkpoint:
  checkpoints/G0B-T02__MACM6__20261001T190551Z__1d2b32d__73b620d2__initial.h5
  SHA256 `462ee5c0e3015d9014b669eabfd78d47b1050e2301961f4a35cb3deb99e792eb`.
- RTX5070 nonstationary checkpoint:
  checkpoints/G0B-T02__RTX5070__20261003T203645Z__1cb2c8a__23ad6ac8__initial.h5
  SHA256 `4e462a0f240fb28f8a21033f07594aa94a73bb51d21eabeb37e0a8015c89d1bb`.
- External PDF/checkpoint hashes remain identical to their existing records;
  none is added to the new commit. Historical numerical evidence is unchanged.
- STATUS.md is generated by scripts/ctl.py refresh, with an early remaining
  work overview and full G0-G6 contract tables.

## Reproduction command
With portable Git on PATH and this workspace trusted by Git:
```powershell
git bundle verify REPOSITORY.bundle
git bundle list-heads REPOSITORY.bundle
Get-FileHash -LiteralPath REPOSITORY.bundle -Algorithm SHA256
git fetch REPOSITORY.bundle refs/heads/codex/macm6-completion:refs/heads/codex/macm6-completion
git fsck --strict --no-reflogs
git rev-list --count codex/macm6-completion
.venv/Scripts/python.exe scripts/ctl.py refresh
.venv/Scripts/python.exe -m unittest discover -s tests/unit -p test_status_dashboard.py
```
To compare an evidence file: `git show codex/macm6-completion:RELATIVE_PATH`
as raw bytes against that file, without checking out the historical branch.

## What changed from previous report
Recovered original MACM6 commit objects and recorded the supplied bundle
identity. The previous CUDA reports correctly describe history availability
at their run time and remain immutable. Only current control-plane views,
readiness/handoff notes and provenance metadata are updated.

## Next action
G0B-T03 on RTX5070: implement the resumable production driver, reproduce the
matched 17^3,21^3,25^3,33^3 stationary sequence under unchanged tolerances;
then G0B-T04 physical Hessian and G0C cross-device/precision checks.
MACM6's two remaining G0 source benchmarks remain TODO plan scope.
G1-G6 full scientific completion remains PARTIAL / UNRESOLVED.

## Handoff references
AGENTS.md, state/state.yaml, STATUS.md, NEXT.md, MACHINE_HANDOFF.md,
docs/RTX5070_READY.md and docs/RTX5070_TRANSFER_PACKET.md.
