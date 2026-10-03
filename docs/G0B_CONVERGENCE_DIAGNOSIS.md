# G0B-T03 - frozen first RTX5070 stationary attempt

Run: G0B-T03__RTX5070__20261003T220757Z__68eddf6__9df9405b.
Exact code commit: 68eddf6; config SHA256:
9df9405b559f40888a11681483375bc59bde622ea2846eee5de3c460b3e8c761.
Report and separate EQUIVALENCE assessment are referenced by NEXT/handoff.

## Observed result

144 unit tests passed; real CUDA float64 derivative/backend checks passed.
The small checkpoint-restarted versus uninterrupted AL solve matched exactly.
Post-report dashboard/failure regressions and the full suite passed 145 tests
in 20.884 seconds; the sealed numerical report retains its original 144 count.
Production ran from a clean tree; four source AL updates and original inner
limits were kept. No evaluation cap was exceeded and no NaN/Inf occurred.

| Row | Energy | Relative energy error | Q_H | Physical constrained RMS | Decision |
|---|---|---|---|---|---|
| 17^3, L=4 | 281.367528242493 | 7.9194e-6 | -0.999998794042 | 1.05284e-6 | Row accepted |
| 21^3, L=4 | 281.275608287190 | 1.60283e-5 | -0.999753990641 | 3.43042e-5 | FAIL residual |
| 25^3, L=4 | N/A | N/A | N/A | N/A | NOT_RUN |
| 33^3, L=8 | N/A | N/A | N/A | N/A | NOT_RUN |

The predeclared physical RMS threshold is 1e-5; energy/charge acceptance
remains 5e-4. 17^3 acceptance is not full task/device completion.

## Smallest discriminating checks already completed

Final 21^3 CPU/CUDA oracle error is 1.98799e-14; analytic/autograd gradient
error is 1.97065e-15. The independent host NumPy physical residual is
3.4304157583518184e-5, matching CUDA 3.430415758356348e-5. Thus the failed
threshold is not explained by a CUDA sign, normalization or tested-gradient
disagreement. This does not exclude every possible shared implementation error.

All four 21^3 inner solves reach 120 iterations (130,127,125,126 evaluations).
The last chart-gradient maximum is 2.85341e-5, above the requested 1e-10
stopping tolerance. The third AL update has RMS 9.82441e-6, but the fourth
raises it to 3.43042e-5. Selecting the third checkpoint or adding updates
would change the configured procedure and must not silently create PASS.

## Classification and next test

Current classification: optimizer stopping/AL conditioning; precise source
initializer and optimizer realization remain unavailable and unresolved.
This is not a robust physical instability or a reason to modify the EFT.
The failed branch's code/config/field are frozen in Git/run evidence and
hashed HDF5 checkpoints. Keep every earlier PASS/FAIL artifact unchanged.

The next narrow RTX5070 diagnostic should measure normalized-chart/radial
conditioning and/or test a source-compatible warm start from the accepted
17^3 field on 21^3, under separately frozen config and explicit equivalence
scope. Do one discriminating change at a time; retain original source limits
and scientific tolerances. Do not launch 25^3/33^3, a Hessian or a wider scan
until the failed residual is resolved and an explicit recovery is recorded.

Measured run totals: 79.6359 s, sampled peak RAM 1.54495 GB, CUDA allocated
peak 0.108329 GB. These are small-grid measurements, not a 97^3/128^3 memory
projection. Twelve ignored checkpoints total 222026688 bytes; every path/hash
is sealed in result.json and included in the SUBSTEP REPORT. CLOUD stays
paused at USD 0; RTX5070 remains the explicit device preference.
