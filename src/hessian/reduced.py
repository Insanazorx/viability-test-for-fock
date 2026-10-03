"""Exact differentiated discrete gradients; no dense Hessian allocation."""
from __future__ import annotations

import math
from core.math_core import SPATIAL_PAIRS
from static.hopf import HopfInvariant


def variations(engine, field, direction):
    engine.check(field);engine.check(direction)
    dn=engine.gradient(field);dv=engine.gradient(direction);ops=engine.ops
    f=engine.core.field_strength(field,dn)
    delta=ops.stack([ops.sum(direction*ops.cross(dn[...,i,:],dn[...,j,:])+
                         field*(ops.cross(dv[...,i,:],dn[...,j,:])+ops.cross(dn[...,i,:],dv[...,j,:])),-1)
                     for i,j in SPATIAL_PAIRS])
    return dn,dv,f,delta


def energy_hvp(engine, field, direction):
    dn,dv,f,df=variations(engine,field,direction);ops=engine.ops
    local=field*0;flux=[dv[...,i,:] for i in range(3)]
    for p,(i,j) in enumerate(SPATIAL_PAIRS):
        a,b=dn[...,i,:],dn[...,j,:];da,db=dv[...,i,:],dv[...,j,:]
        c,dc=f[...,p,None],df[...,p,None]
        local=local+dc*ops.cross(a,b)+c*(ops.cross(da,b)+ops.cross(a,db))
        flux[i]=flux[i]+dc*ops.cross(b,field)+c*(ops.cross(db,field)+ops.cross(b,direction))
        flux[j]=flux[j]+dc*ops.cross(field,a)+c*(ops.cross(direction,a)+ops.cross(field,da))
    return engine.grid.cell_volume*(local-engine.divergence(ops.stack(flux,axis=-2)))


def charge_hvp(engine, field, direction):
    dn,dv,f,df=variations(engine,field,direction);ops=engine.ops;hopf=HopfInvariant(engine)
    a=hopf.from_magnetic(engine.core.magnetic_field(f))['potential']
    da=hopf.from_magnetic(engine.core.magnetic_field(df))['potential']
    c=ops.stack([a[...,2],-a[...,1],a[...,0]])
    dc=ops.stack([da[...,2],-da[...,1],da[...,0]])
    local=field*0;flux=[field*0 for _ in range(3)]
    for p,(i,j) in enumerate(SPATIAL_PAIRS):
        x,y=dn[...,i,:],dn[...,j,:];dx,dy=dv[...,i,:],dv[...,j,:]
        cp,dcp=c[...,p,None],dc[...,p,None]
        local=local+dcp*ops.cross(x,y)+cp*(ops.cross(dx,y)+ops.cross(x,dy))
        flux[i]=flux[i]+dcp*ops.cross(y,field)+cp*(ops.cross(dy,field)+ops.cross(y,direction))
        flux[j]=flux[j]+dcp*ops.cross(field,x)+cp*(ops.cross(direction,x)+ops.cross(field,dx))
    return engine.grid.cell_volume/(8*math.pi**2)*(local-engine.divergence(ops.stack(flux,axis=-2)))


def tangent_frames(engine, field):
    engine.check(field);ops=engine.ops;module=ops.module
    if ops.any(abs(ops.sum(field*field,-1)-1)>1e-12):
        raise ValueError('Tangent frames require a unit field')
    index=module.argmin(abs(field),axis=-1) if ops.name=='numpy' else module.argmin(abs(field),dim=-1)
    axis=ops.as_like([[1.,0.,0.],[0.,1.,0.],[0.,0.,1.]],field)[index]
    first=ops.cross(field,axis);first=first/ops.sqrt(ops.sum(first*first,-1))[...,None]
    return ops.stack([first,ops.cross(field,first)],axis=-2)


class TangentChargeHessian:
    """Hessian of (E-alpha Q)(normalize(n0+e.u)) at u=0.

    Site eigenvalues need division by h^3 for physical L2 normalization. No
    collective mode is removed here; a stationary physical spectrum is later.
    """
    def __init__(self, engine, field, alpha=0.):
        from static.minimizer import SphereChart
        if not math.isfinite(alpha):
            raise ValueError('Explicit finite Lagrange coefficient required')
        self.engine=engine;self.field=field;self.alpha=alpha;self.ops=engine.ops
        self.frames=tangent_frames(engine,field);self.mask=SphereChart(engine).mask_like(field)
        self.gradient=engine.energy_gradient(field)-alpha*HopfInvariant(engine).charge_gradient(field)
        self.q=self.to_coefficients(HopfInvariant(engine).charge_gradient(field))*self.mask[...,None]
        self.qnorm2=self.ops.sum(self.q*self.q,tuple(range(self.q.ndim)))

    def to_coefficients(self, vector):
        return self.ops.sum(self.frames*vector[...,None,:],-1)

    def to_field(self, coefficients):
        self.ops.check(coefficients,(2,))
        if tuple(coefficients.shape)!=(*self.engine.grid.shape,2):
            raise ValueError('Two tangent coordinates on the exact grid required')
        return self.ops.sum(self.frames*coefficients[...,None],-2)*self.mask[...,None]

    def project(self, value):
        value=value*self.mask[...,None]
        if float(self.qnorm2)>1e-30:
            value=value-self.q*self.ops.sum(value*self.q,tuple(range(value.ndim)))/self.qnorm2
        return value

    def apply(self, coefficients, charge_project=True):
        if charge_project:
            coefficients=self.project(coefficients)
        direction=self.to_field(coefficients)
        ambient=energy_hvp(self.engine,self.field,direction)-self.alpha*charge_hvp(self.engine,self.field,direction)
        # Retraction second derivative contributes -n (n.grad) u.
        value=self.to_coefficients(ambient-self.ops.sum(self.field*self.gradient,-1)[...,None]*direction)
        value=value*self.mask[...,None]
        return self.project(value) if charge_project else value
