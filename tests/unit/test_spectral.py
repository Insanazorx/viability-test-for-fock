"""Independent manufactured fields and variation checks for Eq. (65)."""
import math
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from static.spectral import PeriodicGrid, SpectralEnergy, centered_reference_gradient
from analysis.validate_spectral import unit_two_angle


class SpectralTests(unittest.TestCase):
    def grid(self,n=13):
        return PeriodicGrid((n,n,n),(2*math.pi,3*math.pi,4*math.pi))

    def test_invalid_geometry_rejected(self):
        for shape,box in (((3.,4,5),(1,1,1)),((2,3,4),(1,1,1)),((3,4,5),(0,1,1)),
                          ((3,4,5),(True,1,1)),((3,4,5),(float('inf'),1,1))):
            with self.subTest(shape=shape,box=box),self.assertRaises(ValueError):
                PeriodicGrid(shape,box)

    def test_anisotropic_fourier_derivatives(self):
        grid=self.grid()
        x,y,z=grid.numpy_coordinates()
        n=np.stack((np.sin(2*x),np.cos(4*y/3),np.sin(z)),axis=-1)
        exact=np.zeros((*grid.shape,3,3))
        exact[...,0,0]=2*np.cos(2*x)
        exact[...,1,1]=-4/3*np.sin(4*y/3)
        exact[...,2,2]=np.cos(z)
        np.testing.assert_allclose(SpectralEnergy(grid).gradient(n),exact,atol=2e-14)

    def test_nyquist_first_derivative_is_zero(self):
        grid=self.grid(16)
        n=np.broadcast_to((-1.)**np.arange(16)[:,None,None,None],(*grid.shape,3)).copy()
        np.testing.assert_allclose(SpectralEnergy(grid).gradient(n),0,atol=2e-14)

    def test_constant_vacuum_has_zero_energy(self):
        grid=self.grid()
        n=np.zeros((*grid.shape,3));n[...,2]=1
        self.assertLess(sum(SpectralEnergy(grid).energy(n)),1e-25)

    def test_both_published_energy_coefficients(self):
        grid=self.grid()
        n,_,e2,e4=unit_two_angle(grid)
        actual=SpectralEnergy(grid).energy(n)
        np.testing.assert_allclose(actual,(e2,e4),rtol=2e-14)
        self.assertGreater(actual[1],0)

    def test_unit_constraint_is_explicit(self):
        grid=self.grid()
        n=np.ones((*grid.shape,3))
        with self.assertRaises(ValueError):
            SpectralEnergy(grid).energy(n)
        self.assertLess(sum(SpectralEnergy(grid).energy(n,require_unit=False)),1e-25)

    def test_invalid_shape_nonfinite_and_integer_inputs(self):
        grid=self.grid()
        for value in (np.zeros((*grid.shape,6)),np.zeros((*grid.shape,3),dtype=int),
                      np.full((*grid.shape,3),np.nan),np.zeros((3,3,3,3))):
            with self.subTest(shape=value.shape),self.assertRaises(ValueError):
                SpectralEnergy(grid).gradient(value)

    def test_parseval_including_gradient_energy(self):
        grid=self.grid(16)
        n=np.random.default_rng(7).normal(size=(*grid.shape,3))
        engine=SpectralEnergy(grid)
        physical,fourier,e2=engine.parseval(n)
        self.assertAlmostEqual(physical/fourier,1,places=14)
        measured=engine.energy(n,require_unit=False)[0]
        self.assertAlmostEqual(measured/e2,1,places=14)

    def test_skew_adjoint_even_and_odd(self):
        rng=np.random.default_rng(17)
        for size in (9,16):
            grid=self.grid(size)
            engine=SpectralEnergy(grid)
            u=rng.normal(size=(*grid.shape,3));v=rng.normal(size=u.shape)
            du,dv=engine.gradient(u),engine.gradient(v)
            for i in range(3):
                residual=abs(np.sum(u*dv[...,i,:])+np.sum(du[...,i,:]*v))
                self.assertLess(residual/(np.linalg.norm(u)*np.linalg.norm(dv[...,i,:])),1e-14)

    def test_full_discrete_gradient_off_sphere(self):
        grid=self.grid(9)
        engine=SpectralEnergy(grid)
        rng=np.random.default_rng(31)
        n=rng.normal(size=(*grid.shape,3))*.15
        direction=rng.normal(size=n.shape)*.01
        analytic=np.sum(engine.energy_gradient(n)*direction)
        step=1e-5
        fd=(sum(engine.energy(n+step*direction,require_unit=False))-
            sum(engine.energy(n-step*direction,require_unit=False)))/(2*step)
        self.assertLess(abs(analytic-fd)/max(1,abs(analytic)),1e-8)

    def test_independent_centered_derivative_converges(self):
        errors=[]
        for size in (13,25):
            grid=self.grid(size)
            n,exact,_,_=unit_two_angle(grid)
            errors.append(np.linalg.norm(centered_reference_gradient(n,grid)-exact)/np.linalg.norm(exact))
        self.assertGreater(errors[0]/errors[1],3.5)

    def test_float32_policy_preserves_output_dtype(self):
        grid=self.grid(9)
        n,_,_,_=unit_two_angle(grid)
        self.assertEqual(SpectralEnergy(grid).gradient(n.astype(np.float32)).dtype,np.float32)


if __name__=='__main__':
    unittest.main()
