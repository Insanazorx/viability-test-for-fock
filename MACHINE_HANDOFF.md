# MACHINE HANDOFF

from: MACM6
to: MACM6
task: G0B-T02
status: TODO (CPU Hopf reference); G0B-T01 MACM6 PASS
read:
  - AGENTS.md#g0b
  - reports/G0/G0B-T01__G0B-T01__MACM6__20261001T183741Z__5e9474e__8baddf31__REPORT.md
  - docs/G0B_SPECTRAL.md
  - config/benchmark/g0b_t01_macm6.json.yaml
  - config/benchmark/publication.source.yaml
latest_checkpoint: N/A
checkpoint_sha256: N/A
do_next:
  - inspect the publication's initial map and Fourier Hopf prescription for G0B-T02
  - implement Coulomb-gauge inversion and small-grid degree-one/trivial/deformed-map checks
  - freeze a Hopf config and produce an identified MACM6 report before completion
do_not_repeat:
  - G0B-T01 CPU Eq.65 energy and full-grid FFT derivative acceptance passed
  - 66 tests; manufactured 9^3 through 33^3 sequence; separate 16^3 Nyquist audit
  - analytic energy/Parseval/gradient/rotation/translation/vacuum checks passed
known_issue:
  - RTX5070 is explicitly deferred by the user; no CUDA completion flag changed
  - G0A-T02 and G0B-T01 whole tasks still require real CUDA reports
  - no unit Hopf charge, stationary solution, minimization or Hessian is reported yet
  - even-grid Nyquist derivative is zero by convention and unresolved physical modes are excluded
  - periodic collocation products can alias on unresolved fields; future soliton convergence is required
  - source PDF is ignored by Git; retain source-manifest SHA256
  - CLOUD paused; budget zero; remote runners disabled
