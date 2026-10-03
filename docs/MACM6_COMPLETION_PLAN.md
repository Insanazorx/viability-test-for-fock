# MACM6 before RTX5070 — user-directed work program

Instruction received 2026-10-03: complete everything feasible on MACM6 first, then switch to RTX5070. Each item gets a frozen config, identified run/report and its own machine flag. This document is a work inventory; NEXT.md contains exactly one active action.

## Independent work to complete now

1. G0B-T05 engineering preparation: reduced minimizer, boundary/sphere/charge residual, exact matrix-free HVPs and small-grid independent direct-DFT reference. Does not complete G0B-T03/T04 production.
2. G1A CPU mathematical/reference work: unrestricted six-component static functional, derivative/potential gradients and heavy-normal reduction checks. CUDA implementation/comparison stays unfinished.
3. G4A-T02/T03: absent-operator/EOM/field-choice classification and switching/Xi symmetry audit.
4. G4B dark-sector one-loop potential/counterterm and matching diagnostics on declared controlled backgrounds; report concrete matter/portal dependencies explicitly.
5. G4C radiative-status assessment at the precision actually obtained. No baseline model alteration or added protection field.
6. Flat-space bounce source regression and transparent gravity-equation preparation. Scientific gravitational lifetime acceptance remains dependent on viable scales/precursors.
7. Prepare the RTX5070 execution queue and source/reference artifact transfer with hashes.

## Responsibilities requiring unavailable results or inputs

- G0B-T03 source stationary sequence and G0B-T04 physical spectrum: actual RTX5070 work, then MACM6 fits/audits. Do not mark CPU postprocessing done before its input exists.
- G0C-T01 final cross-device comparison / G0C-T02 precision analysis: require actual CUDA/precision measurements. CPU oracle readiness can be validated beforehand.
- G1B/C/D stationary branch fits, physical spectra, scalar charge, unwinding barriers: require converged finite-stiffness GPU states.
- G1E/F/G complete dynamics/collision audits and G2 production analyses: require their preceding stability gates and simulation outputs. Preparatory formulas do not waive these gates.
- G3 physical interactions and G4E compactness: require measured soliton mass/size and production/collision data.
- G4B concrete visible-matter matching: paper does not specify L_m; a dark-sector calculation cannot supply that missing action.
- G4D final gravitational lifetime region: requires retained parameter/scales and the contract's precursor; flat source regression can be prepared independently.
- G5 final implementation and G6 likelihood work: production-derived inputs must exist first.
- G0D remote runners: still optional and disallowed before G0B PASS. CLOUD paused with zero budget.

Finish all mathematically well-defined, available-input work in the first list. Keep the second list explicit rather than invent data, assume completed prerequisites, or call the whole MACM6 program scientifically closed.
