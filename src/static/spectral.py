"""Full-grid periodic FFT discretization of the published Eq. (65).

NumPy is the MACM6 reference; Torch operations preserve CUDA autograd.
See docs/G0B_SPECTRAL.md for normalization, boundaries and Nyquist policy.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

from core.backends import NumpyBackend
from core.math_core import MathCore, SPATIAL_PAIRS


@dataclass(frozen=True)
class PeriodicGrid:
    shape: tuple[int, int, int]
    box: tuple[float, float, float]

    def __post_init__(self):
        if len(self.shape) != 3 or any(type(n) is not int or n < 3 for n in self.shape):
            raise ValueError("Three integer grid sizes >= 3 are required")
        if len(self.box) != 3 or any(isinstance(v, bool) or not isinstance(v, (int, float))
                                   or not math.isfinite(v) or v <= 0 for v in self.box):
            raise ValueError("Three finite positive box lengths are required")
        object.__setattr__(self, "shape", tuple(self.shape))
        object.__setattr__(self, "box", tuple(float(v) for v in self.box))

    @property
    def spacing(self):
        return tuple(length/n for n, length in zip(self.shape, self.box))

    @property
    def cell_volume(self):
        return math.prod(self.spacing)

    @property
    def volume(self):
        return math.prod(self.box)

    def numpy_coordinates(self):
        import numpy as np
        return np.meshgrid(*(np.arange(n, dtype=np.float64)*h-length/2
                             for n, h, length in zip(self.shape, self.spacing, self.box)),
                           indexing="ij")


class SpectralEnergy:
    def __init__(self, grid: PeriodicGrid, backend=None):
        self.grid = grid
        self.ops = NumpyBackend() if backend is None else backend
        self.core = MathCore(self.ops)

    def check(self, field):
        self.ops.check(field, (3,))
        if tuple(field.shape) != (*self.grid.shape, 3):
            raise ValueError("Expected one full-grid channels-last three-component field")

    def fft(self, field):
        if self.ops.name == "numpy":
            return self.ops.module.fft.fftn(field, axes=(0, 1, 2), norm="ortho")
        return self.ops.module.fft.fftn(field, dim=(0, 1, 2), norm="ortho")

    def inverse(self, modes, like):
        if self.ops.name == "numpy":
            return self.ops.module.fft.ifftn(modes, axes=(0, 1, 2), norm="ortho").real.astype(like.dtype)
        return self.ops.module.fft.ifftn(modes, dim=(0, 1, 2), norm="ortho").real.to(dtype=like.dtype)

    def wave_number(self, axis, like):
        n, length = self.grid.shape[axis], self.grid.box[axis]
        values = [(i if i <= n//2 else i-n)*2*math.pi/length for i in range(n)]
        # The unresolved real Nyquist cosine has zero first derivative at the nodes.
        # Zeroing its multiplier preserves reality and discrete skew-adjointness.
        if n % 2 == 0:
            values[n//2] = 0.0
        shape = [1]*like.ndim
        shape[axis] = n
        return self.ops.as_like(values, like).reshape(shape)

    def gradient(self, field):
        self.check(field)
        modes = self.fft(field)
        return self.ops.stack([self.inverse(1j*self.wave_number(i, field)*modes, field)
                               for i in range(3)], axis=-2)

    def divergence(self, flux):
        self.ops.check(flux, (3, 3))
        if tuple(flux.shape) != (*self.grid.shape, 3, 3):
            raise ValueError("Expected flux[..., spatial_axis, component]")
        terms = []
        for i in range(3):
            part = flux[..., i, :]
            terms.append(self.inverse(1j*self.wave_number(i, part)*self.fft(part), part))
        return sum(terms)

    def integrate(self, density):
        return self.grid.cell_volume*self.ops.sum(density, tuple(range(density.ndim)))

    def densities(self, field, require_unit=True, unit_tolerance=1e-12):
        self.check(field)
        if not math.isfinite(unit_tolerance) or unit_tolerance <= 0:
            raise ValueError("Positive unit tolerance required")
        if require_unit and self.ops.any(abs(self.ops.sum(field*field, -1)-1) > unit_tolerance):
            raise ValueError("Normalize the S2 field explicitly before evaluating physical energy")
        return self.core.reduced_energy(field, self.gradient(field))

    def energy(self, field, require_unit=True):
        e2, e4 = self.densities(field, require_unit=require_unit)
        return self.integrate(e2), self.integrate(e4)

    def energy_gradient(self, field):
        """Euclidean gradient dE/dn at nodes, including cell-volume weight.

        This differentiates the same off-S2 polynomial collocation energy.
        Projection onto the pointwise tangent plane is an explicit caller step.
        """
        derivatives = self.gradient(field)
        strength = self.core.field_strength(field, derivatives)
        local = field*0
        flux = [derivatives[..., i, :] for i in range(3)]
        for p, (i, j) in enumerate(SPATIAL_PAIRS):
            di, dj = derivatives[..., i, :], derivatives[..., j, :]
            coefficient = strength[..., p, None]
            local = local + coefficient*self.ops.cross(di, dj)
            flux[i] = flux[i] + coefficient*self.ops.cross(dj, field)
            flux[j] = flux[j] + coefficient*self.ops.cross(field, di)
        return self.grid.cell_volume*(local-self.divergence(self.ops.stack(flux, axis=-2)))

    def parseval(self, field):
        self.check(field)
        real_norm = self.integrate(self.ops.sum(field*field, -1))
        modes = self.fft(field)
        fourier_norm = self.integrate(self.ops.sum(abs(modes)**2, -1))
        gradient_modes = sum(self.ops.sum(abs(self.wave_number(i, field)*modes)**2, -1)
                             for i in range(3))
        return real_norm, fourier_norm, 0.5*self.integrate(gradient_modes)


def centered_reference_gradient(field, grid: PeriodicGrid):
    """Independent NumPy second-order periodic finite differences (not FFT)."""
    import numpy as np
    if not isinstance(field, np.ndarray) or field.shape != (*grid.shape, 3):
        raise ValueError("Expected a NumPy channels-last field on this grid")
    return np.stack([(np.roll(field, -1, axis=i)-np.roll(field, 1, axis=i))/(2*h)
                     for i, h in enumerate(grid.spacing)], axis=-2)
