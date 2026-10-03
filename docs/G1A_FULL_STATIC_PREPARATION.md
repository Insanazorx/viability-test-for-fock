# G1A-T04 — unrestricted six-component CPU engineering reference

User-directed MACM6 preparation before CUDA, separate from G1A-T01/G1B branch-persistence acceptance. No stationary finite-stiffness state is computed. Source Eqs. (20)-(23),(30),(64)-(65), Appendix A.

At fixed final lambda and chi=0, set mu=mu(lambda)>0 and subtract the additive scalar vacuum energy. Six independent packed M components remain unrestricted; neither radius nor Pfaffian is projected. The exact source functional is

`E = integral [Z_M/2 sum_i,c (D_i M_c)^2 + alpha/4(C1-sigma0^2)^2 + mu C2^2 + zeta/(8 sigma0^4) sum_s,i<j |D_i M_s x D_j M_s|^2]`.

Internal Hodge triplets are isometric. D_i uses the previously validated endpoint/full-grid FFT. Gradients are cell-volume-weighted node derivatives. With `star M = grad_M C2`,

`grad V = alpha(C1-sigma0^2) M + 2 mu C2 star M`.

Its directional derivative is `alpha[2(M.v)M+(C1-sigma0^2)v]+2mu[(star M.v)star M+C2 star v]`. The quartic derivative flux differentiates each area `a x b`; the full gradient is `h^3(grad V-div flux)`. Exact matrix-free HVPs differentiate both the local potential and derivative flux; this does not compute a physical spectrum about a stationary state.

At C1=sigma0^2,C2=0 the radial and Pfaffian normal directions have canonical point masses squared `2 alpha sigma0^2/Z_M` and `2 mu sigma0^2/Z_M`; four tangential potential directions are massless. This is an algebraic vacuum check, not a finite-stiffness soliton Hessian pass.

## Reduced normalization

For M_s=sigma0 n_s/sqrt(2), with analytic tangent derivatives of unit n_s, the two-derivative coefficient is `Z_M sigma0^2/4`, and the per-sector area-squared coefficient is `zeta/32`. The positive change `x = ell xi`, `ell = sqrt(zeta/(8 Z_M sigma0^2))`, gives

`E = [sigma0 sqrt(Z_M zeta)/(4 sqrt(2))] sum_s E65[n_s]`.

The source Eq. (66) quotes proportional scales, with normalization constants absorbed into the dimensionless carrier coefficient. This engineering report derives the factors from the implemented Eq. (20)/(30); it does not assign a physical carrier mass.

On a finite FFT grid, the derivative of a pointwise unit field need not be exactly tangent because products alias. The exact algebraic reduction is therefore checked using separately constructed analytic tangent derivatives. The small full-field grid is used for discrete gradient/HVP/rotation tests, not to conceal that aliasing distinction.

## Acceptance

Frozen config: three seeds, 5^3 grid, central steps 1e-3/1e-4/1e-5, positive declared baseline coefficients. Check energy-gradient and HVP directional differences, HVP bilinear symmetry, proper SO(4) energy invariance, exact analytic heavy-normal reduction, zero Fock-vacuum potential and normal mass identities. The backend-neutral implementation accepts NumPy or an actual CUDA Torch backend; CUDA is not executed here.

The existing reduced checkpoint remains an initial analytic map, not a reproduced stationary solution. Its physical lift/G1A-T02 and all G1B continuations/resolution/box tests await valid production states. No stability, barrier, lifetime or abundance acceptance is inferred from this code reference.
