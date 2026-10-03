"""Unrestricted six-M static sector at fixed final lambda, chi=0.

Eq.20/21/30, baseline coefficients only; no radius/Pfaffian projection.
"""
import math
from core.math_core import SPATIAL_PAIRS
from .spectral import SpectralEnergy


class SixComponentStatic:
    def __init__(self,grid,backend=None,*,z_m=1.,alpha=1.,mu=1.,sigma0=1.,zeta=1.):
        if any(not math.isfinite(v) or v<=0 for v in (z_m,alpha,mu,sigma0,zeta)):
            raise ValueError('Explicit positive finite baseline coefficients required')
        self.engine=SpectralEnergy(grid,backend);self.grid=grid;self.ops=self.engine.ops;self.core=self.engine.core
        self.z_m=z_m;self.alpha=alpha;self.mu=mu;self.sigma0=sigma0;self.zeta=zeta

    def check(self,field):
        self.ops.check(field,(6,))
        if tuple(field.shape)!=(*self.grid.shape,6):
            raise ValueError('Six independent components on the declared full grid required')

    def gradient(self,field):
        self.check(field)
        plus,minus=self.core.dual_vectors(field)
        return self.core.from_dual_vectors(self.engine.gradient(plus),self.engine.gradient(minus))

    def divergence(self,flux):
        plus,minus=self.core.dual_vectors(flux)
        return self.core.from_dual_vectors(self.engine.divergence(plus),self.engine.divergence(minus))

    def potential(self,field):
        c1,c2=self.core.c1(field),self.core.c2(field)
        return self.alpha/4*(c1-self.sigma0**2)**2+self.mu*c2*c2

    def potential_gradient(self,field):
        c1,c2=self.core.c1(field),self.core.c2(field)
        return self.alpha*(c1-self.sigma0**2)[...,None]*field+2*self.mu*c2[...,None]*self.core.hodge(field)

    def potential_hvp(self,field,direction):
        star=self.core.hodge(field);dot=self.ops.sum(field*direction,-1);pf_dot=self.ops.sum(star*direction,-1)
        return self.alpha*(2*dot[...,None]*field+(self.core.c1(field)-self.sigma0**2)[...,None]*direction)+2*self.mu*(pf_dot[...,None]*star+self.core.c2(field)[...,None]*self.core.hodge(direction))

    def quartic_flux(self,derivatives,variation=None):
        outputs=[];c=self.zeta/(8*self.sigma0**4)
        sectors=self.core.dual_vectors(derivatives)
        changes=self.core.dual_vectors(variation) if variation is not None else (None,None)
        for d,v in zip(sectors,changes):
            flux=[self.z_m*(v[...,i,:] if v is not None else d[...,i,:]) for i in range(3)]
            for i,j in SPATIAL_PAIRS:
                a,b=d[...,i,:],d[...,j,:];area=self.ops.cross(a,b)
                if v is None:
                    flux[i]=flux[i]+2*c*self.ops.cross(b,area)
                    flux[j]=flux[j]+2*c*self.ops.cross(area,a)
                else:
                    da,db=v[...,i,:],v[...,j,:]
                    delta=self.ops.cross(da,b)+self.ops.cross(a,db)
                    flux[i]=flux[i]+2*c*(self.ops.cross(db,area)+self.ops.cross(b,delta))
                    flux[j]=flux[j]+2*c*(self.ops.cross(delta,a)+self.ops.cross(area,da))
            outputs.append(self.ops.stack(flux,axis=-2))
        return self.core.from_dual_vectors(*outputs)

    def energy(self,field):
        derivatives=self.gradient(field)
        densities={'two_derivative':self.core.static_two_derivative(derivatives,self.z_m),
                   'quartic':self.core.static_quartic(derivatives,self.sigma0,self.zeta),
                   'potential':self.potential(field)}
        return {key:self.engine.integrate(value) for key,value in densities.items()}

    def energy_gradient(self,field):
        return self.grid.cell_volume*(self.potential_gradient(field)-self.divergence(self.quartic_flux(self.gradient(field))))

    def hvp(self,field,direction):
        self.check(field);self.check(direction)
        return self.grid.cell_volume*(self.potential_hvp(field,direction)-self.divergence(self.quartic_flux(self.gradient(field),self.gradient(direction))))
