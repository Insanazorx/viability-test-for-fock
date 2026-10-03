"""Paper Eqs. 4-10, 15-19, 20, 30-31 and 64-68; see docs/MATH_CORE.md."""
from __future__ import annotations

import math

from .backends import NumpyBackend

PAIRS = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
SPATIAL_PAIRS = ((0, 1), (0, 2), (1, 2))
SQRT2 = math.sqrt(2.0)
BASIS = []
for a, b in PAIRS:
    element = [[0.0] * 4 for _ in range(4)]
    element[a][b], element[b][a] = 1.0, -1.0
    BASIS.append(element)
IDENTITY4 = [[float(a == b) for b in range(4)] for a in range(4)]


def positive(value, name):
    if not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and positive")


class MathCore:
    """Channels last; six independent M components, never 16 free components."""

    def __init__(self, backend=None):
        self.ops = backend if backend is not None else NumpyBackend()

    def matrix(self, field):
        self.ops.check(field, (6,))
        return self.ops.einsum("...c,cab->...ab", field, self.ops.as_like(BASIS, field))

    def packed(self, matrix):
        self.ops.check(matrix, (4, 4))
        scale = self.ops.sum(matrix * matrix, (-2, -1)) + 1.0
        defect = self.ops.sum((matrix + matrix.swapaxes(-1, -2)) ** 2, (-2, -1))
        if self.ops.any(defect > 1e-24 * scale):
            raise ValueError("Matrix is not antisymmetric")
        return self.ops.stack([matrix[..., a, b] for a, b in PAIRS])

    def c1(self, field):
        self.ops.check(field, (6,))
        return self.ops.sum(field * field, -1)

    def c2(self, field):
        self.ops.check(field, (6,))
        a, b, c, d, e, f = [field[..., i] for i in range(6)]
        return a * f - b * e + c * d

    def hodge(self, field):
        self.ops.check(field, (6,))
        return self.ops.stack([field[..., 5], -field[..., 4], field[..., 3],
                               field[..., 2], -field[..., 1], field[..., 0]])

    def projections(self, field):
        star = self.hodge(field)
        return 0.5 * (field + star), 0.5 * (field - star)

    def la_vectors(self, field):
        self.ops.check(field, (6,))
        angular = self.ops.stack([field[..., 3], -field[..., 1], field[..., 0]])
        runge = self.ops.stack([field[..., 2], field[..., 4], field[..., 5]])
        return angular, runge

    def dual_vectors(self, field):
        angular, runge = self.la_vectors(field)
        return (angular + runge) / SQRT2, (angular - runge) / SQRT2

    def from_dual_vectors(self, plus, minus):
        self.ops.check(plus, (3,))
        self.ops.check(minus, (3,))
        if plus.shape != minus.shape:
            raise ValueError("Dual vector shapes differ")
        angular, runge = (plus + minus) / SQRT2, (plus - minus) / SQRT2
        return self.ops.stack([angular[..., 2], -angular[..., 1], runge[..., 0],
                               angular[..., 0], runge[..., 1], runge[..., 2]])

    def stf(self, field):
        matrix = self.matrix(field)
        gram = matrix @ matrix.swapaxes(-1, -2)
        return gram - 0.5 * self.c1(field)[..., None, None] * self.ops.as_like(IDENTITY4, field)

    def reduced_fields(self, field):
        """Diagnostic directions/radii; a vanishing sector has no S2 direction."""
        plus, minus = self.dual_vectors(field)
        rp = self.ops.sqrt(self.ops.sum(plus * plus, -1))
        rm = self.ops.sqrt(self.ops.sum(minus * minus, -1))
        if self.ops.any(rp == 0) or self.ops.any(rm == 0):
            raise ValueError("A dual sector vanishes; reduced topology is undefined")
        return plus / rp[..., None], minus / rm[..., None], rp, rm

    def lift_reduced(self, plus, minus, sigma0=1.0, unit_tolerance=1e-12):
        positive(sigma0, "sigma0")
        for direction in (plus, minus):
            self.ops.check(direction, (3,))
            error = self.ops.sum(direction * direction, -1) - 1.0
            if self.ops.any(abs(error) > unit_tolerance):
                raise ValueError("Reduced fields must be explicitly normalized S2 directions")
        return self.from_dual_vectors(sigma0 / SQRT2 * plus, sigma0 / SQRT2 * minus)

    def static_two_derivative(self, derivatives, z_m=1.0):
        """Eq. 20: Z_M/4 sum_{i,a,b} (d_i M_ab)^2, gradients (...,3,6)."""
        self.ops.check(derivatives, (3, 6))
        positive(z_m, "z_m")
        return 0.5 * z_m * self.ops.sum(derivatives * derivatives, (-2, -1))

    def static_quartic(self, derivatives, sigma0=1.0, zeta=1.0):
        """Minus static Eq. 30, using isometric dual triplets; no radial penalty."""
        self.ops.check(derivatives, (3, 6))
        positive(sigma0, "sigma0")
        positive(zeta, "zeta")
        terms = []
        for sector in self.dual_vectors(derivatives):
            for i, j in SPATIAL_PAIRS:
                area = self.ops.cross(sector[..., i, :], sector[..., j, :])
                terms.append(self.ops.sum(area * area, -1))
        return zeta / (8.0 * sigma0 ** 4) * self.ops.sum(self.ops.stack(terms), -1)

    def field_strength(self, direction, derivatives):
        """F_ij in order (F12,F13,F23), Eq. 31; off-S2 polynomial extension."""
        self.ops.check(direction, (3,))
        self.ops.check(derivatives, (3, 3))
        if direction.shape[:-1] != derivatives.shape[:-2]:
            raise ValueError("Field and derivative sample shapes differ")
        return self.ops.stack([self.ops.sum(direction * self.ops.cross(
            derivatives[..., i, :], derivatives[..., j, :]), -1) for i, j in SPATIAL_PAIRS])

    def reduced_energy(self, direction, derivatives):
        """Separate densities (e2,e4) with the exact dimensionless Eq. 65 factors."""
        strength = self.field_strength(direction, derivatives)
        return (0.5 * self.ops.sum(derivatives * derivatives, (-2, -1)),
                0.5 * self.ops.sum(strength * strength, -1))

    def magnetic_field(self, field_strength):
        """B_i=epsilon_ijk F_jk/2, epsilon123=+1 (Eq. 67)."""
        self.ops.check(field_strength, (3,))
        return self.ops.stack([field_strength[..., 2], -field_strength[..., 1], field_strength[..., 0]])

    def hopf_functional(self, potential, magnetic, cell_volume):
        """Eq. 68 helicity integral; caller must supply a valid curl potential."""
        self.ops.check(potential, (3,))
        self.ops.check(magnetic, (3,))
        if potential.shape != magnetic.shape:
            raise ValueError("A and B shapes differ")
        positive(cell_volume, "cell_volume")
        density = self.ops.sum(potential * magnetic, -1)
        return cell_volume / (16.0 * math.pi ** 2) * self.ops.sum(density, tuple(range(density.ndim)))
