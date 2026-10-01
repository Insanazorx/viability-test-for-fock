"""Independent smooth compact unit-Hopf fixture; not an archived paper state."""
from __future__ import annotations

import math
import numpy as np

from .spectral import PeriodicGrid


def compact_hopf(grid:PeriodicGrid,scale=1.2,radius=3.4,coordinates=None):
    if not math.isfinite(scale) or scale<=0 or not math.isfinite(radius) or radius<=0:
        raise ValueError('Positive finite profile scale/radius required')
    x=grid.numpy_coordinates() if coordinates is None else coordinates
    if len(x)!=3 or any(np.shape(value)!=grid.shape or not np.isfinite(value).all() for value in x):
        raise ValueError('Three finite full-grid coordinates required')
    s=sum(value*value for value in x)
    inside=s<radius*radius
    g=np.zeros_like(s);gp=np.zeros_like(s)
    gap=radius*radius-s[inside]
    g[inside]=scale*np.exp(-s[inside]/gap)
    gp[inside]=-g[inside]*radius*radius/gap**2  # derivative with respect to r^2
    denominator=s+g*g
    # At r=0, denominator=scale^2; outside support r>0.
    q0=(s-g*g)/denominator
    v=2*g/denominator
    q=np.stack([q0,*(v*value for value in x)],axis=-1)
    q0s=(2*g*g-4*s*g*gp)/denominator**2
    vs=2*(gp*denominator-g*(1+2*g*gp))/denominator**2
    dq=np.stack([np.stack([2*x[i]*q0s,*(v*(i==j)+2*x[i]*x[j]*vs for j in range(3))],axis=-1)
                 for i in range(3)],axis=-2)
    a,b,c,d=[q[...,j] for j in range(4)]
    # Antipodal standard Hopf projection gives the paper's south-pole vacuum.
    n=-np.stack([2*(a*b+c*d),2*(d*b-a*c),a*a+d*d-b*b-c*c],axis=-1)
    da,db,dc,dd=[dq[...,j] for j in range(4)]
    dn=-np.stack([2*(da*b[...,None]+a[...,None]*db+dc*d[...,None]+c[...,None]*dd),
                  2*(dd*b[...,None]+d[...,None]*db-da*c[...,None]-a[...,None]*dc),
                  2*(a[...,None]*da+d[...,None]*dd-b[...,None]*db-c[...,None]*dc)],axis=-1)
    # F=n.dn×dn = dA with A=+2(-i z† dz), z=(q0+i q3,q1+i q2).
    potential=2*(a[...,None]*dd-d[...,None]*da+b[...,None]*dc-c[...,None]*db)
    degree_density=np.linalg.det(np.stack([q,dq[...,0,:],dq[...,1,:],dq[...,2,:]],axis=-2))/(2*math.pi**2)
    return {'field':n,'derivatives':dn,'quaternion':q,'quaternion_derivatives':dq,
            'analytic_potential':potential,'degree_density':degree_density,'bump':g/scale}


def continuum_degree(scale,radius):
    """Independent radial S3 winding integral; its orientation is fixed at -1."""
    from scipy.integrate import quad

    def integrand(r):
        if r==0 or r>=radius:
            return 0.
        s=r*r;gap=radius*radius-s
        g=scale*math.exp(-s/gap)
        gp=-g*radius*radius/gap**2
        denominator=s+g*g
        return 2/math.pi*8*g*g*s*(2*s*gp-g)/denominator**3
    value,error=quad(integrand,0,radius,epsabs=1e-11,epsrel=1e-11,limit=150)
    return {'degree':value,'quadrature_error_estimate':error}
