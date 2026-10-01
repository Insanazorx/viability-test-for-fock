"""Coulomb Fourier inversion and Eq. (68); diagnostics expose lost flux/closure."""
from __future__ import annotations

import math

from core.math_core import SPATIAL_PAIRS
from .spectral import SpectralEnergy


class HopfInvariant:
    def __init__(self, engine: SpectralEnergy):
        self.engine=engine
        self.ops=engine.ops
        self.core=engine.core

    def total(self,value):
        return self.ops.sum(value,tuple(range(value.ndim)))

    def cross_modes(self,k,modes):
        # Explicit components allow real k times complex Torch modes.
        return self.ops.stack([k[...,1]*modes[...,2]-k[...,2]*modes[...,1],
                               k[...,2]*modes[...,0]-k[...,0]*modes[...,2],
                               k[...,0]*modes[...,1]-k[...,1]*modes[...,0]])

    def wave_vectors(self,like):
        zero=like[...,0]*0
        return self.ops.stack([self.engine.wave_number(i,like)[...,0]+zero for i in range(3)])

    def curl(self,potential):
        d=self.engine.gradient(potential)
        return self.ops.stack([d[...,1,2]-d[...,2,1],d[...,2,0]-d[...,0,2],d[...,0,1]-d[...,1,0]])

    def vector_divergence(self,field):
        d=self.engine.gradient(field)
        return d[...,0,0]+d[...,1,1]+d[...,2,2]

    def from_magnetic(self,magnetic):
        """Return A and diagnostics; harmonic/longitudinal B is never certified."""
        self.engine.check(magnetic)
        modes=self.engine.fft(magnetic)
        k=self.wave_vectors(magnetic)
        k2=self.ops.sum(k*k,-1)
        denominator=k2+(k2==0)
        ahat=1j*self.cross_modes(k,modes)/denominator[...,None]*(k2>0)[...,None]
        potential=self.engine.inverse(ahat,magnetic)
        norm=self.ops.sqrt(self.total(magnetic*magnetic))
        safe=norm+(norm==0)
        scale=2*math.pi/min(self.engine.grid.box)
        residual=self.ops.sqrt(self.total((self.curl(potential)-magnetic)**2))/safe
        divergence=self.ops.sqrt(self.total(self.vector_divergence(magnetic)**2))/(scale*safe)
        anorm=self.ops.sqrt(self.total(potential*potential))
        asafe=anorm+(anorm==0)
        gauge=self.ops.sqrt(self.total(self.vector_divergence(potential)**2))/(scale*asafe)
        harmonic=self.ops.sqrt(self.total(abs(modes)**2*(k2==0)[...,None]))/safe
        q=self.core.hopf_functional(potential,magnetic,self.engine.grid.cell_volume)
        fourier_q=self.engine.grid.cell_volume/(16*math.pi**2)*self.total((ahat.conj()*modes).real)
        diagnostics={'curl_relative':residual,'divergence_relative':divergence,'gauge_relative':gauge,
                     'harmonic_fraction':harmonic,'fourier_charge_difference':abs(q-fourier_q)}
        return {'charge':q,'potential':potential,'magnetic':magnetic,'diagnostics':diagnostics}

    def evaluate(self,field,require_unit=True):
        self.engine.check(field)
        if require_unit and self.ops.any(abs(self.ops.sum(field*field,-1)-1)>1e-12):
            raise ValueError('Hopf topology requires an explicitly normalized S2 field')
        strength=self.core.field_strength(field,self.engine.gradient(field))
        return self.from_magnetic(self.core.magnetic_field(strength))

    def charge_gradient(self,field):
        """Euclidean gradient of the same off-S2 discrete helicity polynomial."""
        result=self.evaluate(field,require_unit=False)
        potential=result['potential']
        coefficients=self.ops.stack([potential[...,2],-potential[...,1],potential[...,0]])
        derivatives=self.engine.gradient(field)
        local=field*0
        flux=[field*0 for _ in range(3)]
        for p,(i,j) in enumerate(SPATIAL_PAIRS):
            di,dj=derivatives[...,i,:],derivatives[...,j,:]
            c=coefficients[...,p,None]
            local=local+c*self.ops.cross(di,dj)
            flux[i]=flux[i]+c*self.ops.cross(dj,field)
            flux[j]=flux[j]+c*self.ops.cross(field,di)
        return self.engine.grid.cell_volume/(8*math.pi**2)*(local-self.engine.divergence(self.ops.stack(flux,axis=-2)))
