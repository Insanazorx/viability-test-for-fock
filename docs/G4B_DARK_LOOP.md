# G4B available-input one-loop calculation

Source Eqs.20-24 and p.13. All eight homogeneous scalar fields (six packed M, lambda, chi) enter the exact gradient/Hessian. The canonical mass matrix is K^-1/2 V'' K^-1/2 with K=diag(Z_M repeated six times,1,1). At the Fock vacuum M12=sigma0, chi=0, lambda=lambda_v it has four tangent zeros and squared masses 2 alpha sigma0 squared/Z_M, 2 mu(lambda_v) sigma0 squared/Z_M, U''(lambda_v), m_chi squared-kappa lambda_v squared. Finite-background M/lambda and chi/lambda mixing is retained; chi linear mixing vanishes at chi=0.

For constant backgrounds and zero external matter overlap the scalar determinant is

Delta V = sum_i y_i squared [log(y_i/Q squared)-3/2]/(64 pi squared), y_i=m_i squared.

This is the scalar MSbar formula of [Martin, hep-ph/0111209, Eqs.1.1-1.3 and 3.2](https://arxiv.org/html/hep-ph/0111209). Each real scalar has one degree of freedom. Zero masses contribute their continuous y squared log(y) limit; any negative eigenvalue rejects the real-potential evaluation. No abs-mass or arbitrary eigenvalue clamp hides an unstable background. Only the UV pole functional remains real on off-shell negative-curvature backgrounds.

In d=4-2 epsilon the counterterm has +Tr[(canonical V'') squared]/(64 pi squared epsilon_bar) to cancel the negative bare determinant pole. The explicit scale derivative of Delta V is -Tr[(canonical V'') squared]/(32 pi squared). Running/matching counterterms must cancel it to the computed order; plotting bare loop scale changes is not an RG-improved prediction. The source nonpolynomial functions generate an EFT tower; the d<=4 basis is not claimed closed under all these interactions.

At lambda=chi=0 the chi threshold gives

Delta m_lambda squared = -kappa m_chi squared [log(m_chi squared/Q squared)-1]/(16 pi squared).

For a field-dependent scalar squared mass y(lambda), Delta V'=y y'[log(y/Q squared)-1]/(32 pi squared) and Delta V''=[y' squared log(y/Q squared)+y y''(log(y/Q squared)-1)]/(32 pi squared). The U cubic generates a scalar tadpole and curvature correction; neither is protected by lambda parity.

Let mu4=mu_v/(f*x_mu)^4. The lambda Hessian contains 12 mu4 lambda squared C2 squared. Its determinant expands with Delta V proportional to 12 mu4 lambda squared C2 squared U''(lambda)[log(U''/Q squared)-1]/(32 pi squared). The UV-pole numerator has 24 mu4 U''(0) lambda squared C2 squared. Equal-C1/different-C2 backgrounds and symmetric small-lambda differences independently verify this coefficient. A lower quadratic switching onset is therefore actually generated in this computed diagram, not merely symmetry allowed. A constant/linear onset is not asserted at this one-loop order; higher loops and UV matching remain independent questions. No correction is inserted into the baseline solver.

Renormalization conditions must specify V_eff(lambda_v), V_eff'(lambda_v)=0, V_eff''(lambda_v), and mu_eff derivatives at zero through order three at a declared matching scale. Xi Taylor coefficients and derivative/curvature/portal Wilson coefficients need their own matching inputs. The absolute vacuum density cannot be discarded when gravity is included.

With a Euclidean hard cutoff, the same chi tadpole instead gives -kappa [Lambda_cut squared-m_chi squared log(1+Lambda_cut squared/m_chi squared)]/(16 pi squared). This is an explicit matching-sensitivity diagnostic, not a scheme-independent observable. Conditional tuning measures are |Delta V|/rho_target and |Delta m_lambda squared|/m_lambda,target squared after declaring the renormalization/matching prescription. The supplied dimensionless test coefficients and scale sweep are illustrative verification fixtures; their cancellation ratios are not physical DE tuning estimates.

The first-derivative quartic M term has no quadratic fluctuation term at a constant M background. With zero matter overlap, the portal and STF composite begin beyond the quadratic determinant. This does not set their finite-momentum or higher-loop matching corrections to zero. Curvature, kinetic, portal-induced corrections, matter fluctuations, and a full controlled UV matching packet are unfinished because L_m, physical f/Lambda_U/sigma0/m_chi/portal Lambda, the cutoff and retained parameter region have not been supplied. Completion of this scoped dark-sector calculation does not close all of Gate4-B.

The baseline is radiatively tuned in the computed sector. Technical naturalness is not established; viability remains PARTIAL / UNRESOLVED. No extra protection mechanism or new theory branch is introduced.
