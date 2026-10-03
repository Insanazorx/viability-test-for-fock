"""Small odd-grid direct DFT reference; no FFT/core/Hopf backend reuse."""
import math
import numpy as np


def direct_observables(field, spacing):
    if not isinstance(field,np.ndarray) or field.ndim!=4 or not np.isfinite(field).all():
        raise ValueError('Finite four-dimensional NumPy field required')
    if not math.isfinite(spacing) or spacing<=0:
        raise ValueError('Positive finite spacing required')
    n=field.shape[0]
    if field.shape!=(n,n,n,3) or n%2!=1 or n>9:
        raise ValueError('Direct reference is deliberately restricted to odd cubic grids <=9')
    sites=np.stack(np.meshgrid(*([np.arange(n)]*3),indexing='ij'),axis=-1).reshape(-1,3)
    integers=np.where(np.arange(n)<=n//2,np.arange(n),np.arange(n)-n)
    modes=np.stack(np.meshgrid(*([integers]*3),indexing='ij'),axis=-1).reshape(-1,3)
    waves=2*math.pi*modes/(n*spacing)
    transform=np.exp(-2j*math.pi*(modes@sites.T)/n)/math.sqrt(n**3)
    inverse=transform.conj().T
    # Explicit sums keep this reference simple and avoid complex BLAS flags
    # observed in the frozen macOS NumPy build, rather than suppress warnings.
    multiply=lambda a,b:np.einsum('ij,jc->ic',a,b,optimize=False)
    coefficients=multiply(transform,field.reshape(-1,3))
    derivatives=np.stack([multiply(inverse,1j*waves[:,i,None]*coefficients).real for i in range(3)],axis=-2)
    value=field.reshape(-1,3)
    strength=np.stack([np.sum(value*np.cross(derivatives[:,i,:],derivatives[:,j,:]),axis=-1)
                       for i,j in ((0,1),(0,2),(1,2))],axis=-1)
    e2=0.5*spacing**3*np.sum(derivatives**2);e4=0.5*spacing**3*np.sum(strength**2)
    magnetic=np.stack([strength[:,2],-strength[:,1],strength[:,0]],axis=-1)
    bhat=multiply(transform,magnetic);k2=np.sum(waves**2,axis=-1)
    ahat=1j*np.cross(waves,bhat)/(k2+(k2==0))[:,None]*(k2>0)[:,None]
    potential=multiply(inverse,ahat).real
    charge=spacing**3*np.sum(potential*magnetic)/(16*math.pi**2)
    return dict(energy=float(e2+e4),energy2=float(e2),energy4=float(e4),charge=float(charge))
