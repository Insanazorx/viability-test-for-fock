# MACM6 reduced solver/Hessian preparation — G0B-T05

This engineering substep prepares G0B-T03/T04 and G0C-T01 while preserving their scientific order/completion flags. User instruction on 2026-10-03: finish all feasible MACM6 responsibilities before RTX5070. The published stationary sequence remains assigned to RTX5070 first.

## Mathematical contract

Use the endpoint-included grid, h=2L/(N-1), FFT period Nh, fixed south-pole boundary. For each interior raw vector x, n=x/|x|. Every oracle evaluation reprojects pointwise, not just accepted iterations. Its Jacobian pulls back a node gradient g as `(g-n(n.g))/|x|`. Raw x=0 is a rejected chart singularity. Boundary variables are excluded from the optimizer.

Eq. (70): `F=E+l(Q-Qstar)+beta/2 (Q-Qstar)^2`, `grad F=grad E+[l+beta(Q-Qstar)] grad Q`, `l_next=l+beta(Q-Qstar)`. Each outer solve recenters the raw chart on the normalized result. This introduces redundant radial coordinates inside an optimizer chart; it does not add physical degrees of freedom.

The physical constrained residual projects both node gradients into local sphere tangents, masks the boundary, and subtracts the component along the projected charge gradient. The RMS residual divides node gradients by the cell volume h^3. A rank-zero charge gradient is recorded as such; it is not silently promoted to an independent constraint. The Hessian uses the distinct functional E-alpha Q and its charge projection.

For F_ij=n.(D_i n x D_j n), differentiate all three factors. The exact directional Hessian products differentiate the already validated off-sphere collocation energy/charge gradients, including the linear Coulomb inverse for delta B. No dense Hessian is allocated. In a fixed local orthonormal frame e_a at n0, the normalized chart has

`H_chart u = e^T [H_ambient(e u) - (n0.grad(E-alpha Q)) e u]`.

Charge projection applies to both input and output. The boundary is fixed. Site-normalized eigenvalues would require division by h^3 for physical L2 normalization. No collective mode is deflated and no stationary physical spectrum is claimed in this preparation run.

## Independent reference

`direct_reference.py` builds full direct DFT matrices from integer mode/site indices on odd grids <=9. It does not call FFTs, MathCore, SpectralEnergy or HopfInvariant. It independently constructs derivatives, F, B, Coulomb inversion and helicity. Centered directional differences of this oracle check energy and charge gradients. Ambient HVPs are checked against differences of gradients and bilinear symmetry. Retraction HVPs are checked against independently differentiated chart gradients.

The compact Hopf field is independently derived. A 5^3 charge is deliberately **not** certified as resolved unit topology. Small-grid oracle checks test the mathematical discretization, not the published stationary energy.

## Solver adapters and source settings

The paper section 7.1 records four outer updates, beta=2e4, at most 120 inner iterations/180 evaluations, gradient tolerance 1e-10 and change tolerance 1e-14. The CUDA adapter uses Torch LBFGS with strong_wolfe and explicit analytic gradients; CUDA remains unexecuted on MACM6. The independent CPU adapter uses unbounded SciPy L-BFGS-B with a sphere chart. It has separate engineering/equivalence scope; production reproduction tolerances are unchanged.

Primary software references: [SciPy L-BFGS-B](https://docs.scipy.org/doc/scipy-1.16.2/reference/optimize.minimize-lbfgsb.html), [PyTorch LBFGS](https://docs.pytorch.org/docs/stable/generated/torch.optim.LBFGS.html). The observed SciPy package version is frozen as 1.16.3; the cited minor-series API documents the used options. Optimizer success/termination messages and actual counts are recorded, rather than treating max-iteration termination as convergence.

Smoke solves start in a small contractible vacuum neighborhood with Qstar=0, grid 9^3. Acceptance checks energy reduction, physical residual, fixed boundary, unit norm, multiplier updates, and derivative/reference consistency. They establish plumbing and a converged trivial solution, not Hopfion existence. Source 17^3/21^3/25^3/33^3 energies and |Q|-1 <=5e-4 remain G0B-T03 production targets.
