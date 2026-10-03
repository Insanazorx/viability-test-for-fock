# Source bounce regression and CDL equation preparation

Read source p.7 Eqs.50-51: a=.24,b=c=1,x_false=.6,u_false=.0036; x(0)=.00116696542914; Bhat4=1082.94756088. The archived source field is not required for the independent shooting calculation. Its reported virial defect1.88e-9 and truncation shift5.96e-6 are comparison diagnostics; the frozen preparation tolerances are independently stated, not silently substituted into the published table.

Flat O(4) equation: x''+3x'/rho=u'(x). Regular origin: x=x0+u'(x0)rho squared/8+O(rho^4), x'=u'(x0)rho/4+O(rho^3). Transparent DOP853 overshoot/undershoot integration and bracket bisection are repeated at three tolerances. Kinetic and subtracted potential action integrals are integrated alongside the field. The shooting events classify genuine overshoot/undershoot; no solution is assumed simply from the published initial number. The endpoint field/derivative and the virial condition2T+4V=0 diagnose the tail. B4=(f/Lambda_U)^4 Bhat4; no years/prefactor are inferred.

For Euclidean ds squared=drho squared+r(rho) squared dOmega3 squared, epsilon=f squared/M_Pl squared, minimally coupled gravity gives

- x'=p; p'=u'(x)-3 r' p/r;
- r''=-epsilon r [p squared+u]/3;
- (r') squared=1+epsilon r squared [p squared/2-u]/3.

Near a regular pole, r=rho-epsilon u(x0)rho cubed/18+... and x has the flat-origin quadratic term. At the second compact pole, regular scalar derivative vanishes. Positive false-vacuum energy means a compact geometry; copying the flat infinite-radius shooting boundary is insufficient.

The on-shell dimensionless action is4 pi squared integral[r cubed u-3r/epsilon] drho. The physical action multiplies(f/Lambda_U)^4. The constant false vacuum has H squared=epsilon u_false/3, r=sin(H rho)/H, and S_false=-24 pi squared/(epsilon squared u_false). Bounce B requires subtracting this action consistently. At epsilon=0 the compact false-vacuum formula is singular and must not be used; the separate flat equation is implemented.

These equations follow the [Coleman–De Luccia original paper, Phys.Rev.D21,3305](https://journals.aps.org/prd/abstract/10.1103/PhysRevD.21.3305). In this preparation we verify constraint conservation, the flat limit, and the constant-false-vacuum geometry/action numerically. A nontrivial compact gravitational bounce and prefactor are not solved. Physical scales, retained parameter region and G1B precursor are absent; scientific G4D lifetime acceptance remains pending. G4D-T04 is explicitly preparation, so it does not waive those dependencies or complete G4D-T01..T03.
