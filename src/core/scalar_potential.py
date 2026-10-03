"""Exact homogeneous source Eq.21/22/24, NumPy float64 reference."""
from dataclasses import dataclass
import numpy as np
from .math_core import MathCore


@dataclass(frozen=True)
class ScalarPotential:
    z_m: float = 1.
    alpha: float = 1.
    sigma0: float = 1.
    mu_v: float = 1.
    f: float = 1.
    x_mu: float = .5
    lambda_u: float = 1.
    a: float = .24
    b: float = 1.
    c: float = 1.
    m_chi2: float = 2.
    eta: float = .1
    kappa: float = .1
    chi_s: float = 1.

    def __post_init__(self):
        if any(not np.isfinite(v) or v<=0 for v in self.__dict__.values()):
            raise ValueError('Source coefficients/scales must be finite and positive')

    def mu(self,lam):
        d=self.f*self.x_mu;t=(lam/d)**4;e=np.exp(-t)
        first=4*lam**3/d**4;second=12*lam**2/d**4
        return (-self.mu_v*np.expm1(-t),self.mu_v*e*first,self.mu_v*e*(second-first*first))

    def xi(self,chi):
        y2=(chi/self.chi_s)**2
        return (chi**2/(1+y2),2*chi/(1+y2)**2,2*(1-3*y2)/(1+y2)**3)

    def u(self,lam):
        x=lam/self.f;s=self.lambda_u**4
        return (s*(self.a*x*x/2-self.b*x**3/3+self.c*x**4/4),
                s/self.f*(self.a*x-self.b*x*x+self.c*x**3),
                s/self.f**2*(self.a-2*self.b*x+3*self.c*x*x),
                s/self.f**3*(-2*self.b+6*self.c*x),6*s*self.c/self.f**4)

    def evaluate(self,fields):
        fields=np.asarray(fields,dtype=np.float64)
        if fields.shape!=(8,) or not np.all(np.isfinite(fields)):
            raise ValueError('Six M components, lambda, chi required')
        m=fields[:6];lam,chi=fields[6:];core=MathCore();star=core.hodge(m)
        c1=float(core.c1(m));c2=float(core.c2(m));mu,dm,ddm=self.mu(lam)
        xi,dx,ddx=self.xi(chi);u,du,ddu,_,_=self.u(lam)
        value=self.alpha/4*(c1-self.sigma0**2)**2+mu*c2*c2+u+self.m_chi2*chi**2/2+self.eta*chi**4/4-self.kappa*xi*lam**2/2
        gradient=np.r_[self.alpha*(c1-self.sigma0**2)*m+2*mu*c2*star,dm*c2*c2+du-self.kappa*xi*lam,self.m_chi2*chi+self.eta*chi**3-self.kappa*dx*lam**2/2]
        hessian=np.zeros((8,8))
        hessian[:6,:6]=self.alpha*(2*np.outer(m,m)+(c1-self.sigma0**2)*np.eye(6))+2*mu*(np.outer(star,star)+c2*core.hodge(np.eye(6)))
        hessian[:6,6]=hessian[6,:6]=2*dm*c2*star
        hessian[6,6]=ddm*c2*c2+ddu-self.kappa*xi
        hessian[7,7]=self.m_chi2+3*self.eta*chi**2-self.kappa*ddx*lam**2/2
        hessian[6,7]=hessian[7,6]=-self.kappa*dx*lam
        normalization=np.r_[np.full(6,1/np.sqrt(self.z_m)),1.,1.]
        canonical=hessian*normalization[:,None]*normalization[None,:]
        return float(value),gradient,hessian,canonical
