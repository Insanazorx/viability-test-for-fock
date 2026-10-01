"""Independent sign, harmonic-flux, curvature and discrete-variation checks."""
import math
from pathlib import Path
import sys
import unittest

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'src'))
from static.spectral import PeriodicGrid,SpectralEnergy
from static.hopf import HopfInvariant
from static.hopf_initial import compact_hopf,continuum_degree


class HopfTests(unittest.TestCase):
    def engine(self,size=17):
        return SpectralEnergy(PeriodicGrid.paper(size,4.))

    def test_paper_spacing_period_and_endpoints(self):
        grid=PeriodicGrid.paper(17,4.)
        self.assertEqual(grid.spacing,(.5,)*3)
        self.assertEqual(grid.box,(8.5,)*3)
        x,_,_=grid.numpy_coordinates()
        self.assertEqual(x[0,0,0],-4.)
        self.assertEqual(x[-1,0,0],4.)

    def test_map_is_unit_and_exact_boundary_vacuum(self):
        engine=self.engine()
        data=compact_hopf(engine.grid)
        np.testing.assert_allclose(np.sum(data['field']**2,-1),1,atol=2e-15)
        np.testing.assert_allclose(np.sum(data['quaternion']**2,-1),1,atol=2e-15)
        for i in range(3):
            for end in (0,-1):
                face=np.take(data['field'],end,axis=i)
                np.testing.assert_allclose(face,np.broadcast_to([0,0,-1],face.shape),atol=0)

    def test_analytic_profile_derivatives(self):
        grid=PeriodicGrid.paper(9,4.)
        x=grid.numpy_coordinates()
        data=compact_hopf(grid)
        for i in range(3):
            shifted=[]
            for sign in (-1,1):
                coordinates=[v+sign*1e-5*(i==j) for j,v in enumerate(x)]
                shifted.append(compact_hopf(grid,coordinates=coordinates)['field'])
            np.testing.assert_allclose((shifted[1]-shifted[0])/2e-5,data['derivatives'][...,i,:],atol=2e-9)

    def test_radial_winding_fixes_orientation(self):
        result=continuum_degree(1.2,3.4)
        self.assertLess(abs(result['degree']+1),1e-12)
        self.assertLess(result['quadrature_error_estimate'],1e-10)

    def test_independent_berry_helicity_equals_winding_density(self):
        engine=self.engine()
        data=compact_hopf(engine.grid)
        b=engine.core.magnetic_field(engine.core.field_strength(data['field'],data['derivatives']))
        helicity=np.sum(data['analytic_potential']*b,-1)/(16*math.pi**2)
        np.testing.assert_allclose(helicity,data['degree_density'],atol=2e-16)

    def test_helical_potential_and_helicity_sign(self):
        engine=self.engine();_,_,z=engine.grid.numpy_coordinates()
        k=2*math.pi/engine.grid.box[2]
        a=np.stack([np.cos(k*z),np.sin(k*z),z*0],axis=-1)
        data=HopfInvariant(engine).from_magnetic(-k*a)
        np.testing.assert_allclose(data['potential'],a,atol=4e-15)
        self.assertLess(abs(data['charge']+k*engine.grid.volume/(16*math.pi**2)),1e-13)
        self.assertLess(data['diagnostics']['gauge_relative'],1e-13)

    def test_harmonic_flux_cannot_be_a_periodic_curl(self):
        engine=self.engine();b=np.zeros((*engine.grid.shape,3));b[...,2]=1
        data=HopfInvariant(engine).from_magnetic(b)
        self.assertAlmostEqual(data['diagnostics']['harmonic_fraction'],1,places=14)
        self.assertAlmostEqual(data['diagnostics']['curl_relative'],1,places=14)

    def test_longitudinal_field_is_exposed(self):
        engine=self.engine();x,_,_=engine.grid.numpy_coordinates()
        b=np.zeros((*engine.grid.shape,3));b[...,0]=np.sin(2*math.pi*x/engine.grid.box[0])
        data=HopfInvariant(engine).from_magnetic(b)
        self.assertAlmostEqual(data['diagnostics']['curl_relative'],1,places=14)
        self.assertGreater(data['diagnostics']['divergence_relative'],.99)

    def test_trivial_great_circle_map_has_zero_charge(self):
        engine=self.engine();bump=compact_hopf(engine.grid)['bump']
        n=np.stack([np.sin(.3*bump),bump*0,-np.cos(.3*bump)],axis=-1)
        self.assertEqual(HopfInvariant(engine).evaluate(n)['charge'],0)

    def test_spatial_reflection_flips_hopf_sign(self):
        engine=self.engine();n=compact_hopf(engine.grid)['field'];hopf=HopfInvariant(engine)
        q=hopf.evaluate(n)['charge']
        reflected=hopf.evaluate(np.flip(n,axis=0).copy())['charge']
        self.assertLess(abs(q+reflected),1e-13)
        self.assertLess(q,0)

    def test_target_antipodal_preserves_hopf_charge(self):
        engine=self.engine();n=compact_hopf(engine.grid)['field'];hopf=HopfInvariant(engine)
        self.assertLess(abs(hopf.evaluate(n)['charge']-hopf.evaluate(-n)['charge']),1e-13)

    def test_charge_gradient_of_off_sphere_polynomial(self):
        engine=self.engine(9);hopf=HopfInvariant(engine);rng=np.random.default_rng(11)
        n=rng.normal(size=(*engine.grid.shape,3))*.2
        direction=rng.normal(size=n.shape)*.03
        analytic=np.sum(hopf.charge_gradient(n)*direction)
        step=1e-5
        fd=(hopf.evaluate(n+step*direction,require_unit=False)['charge']-
            hopf.evaluate(n-step*direction,require_unit=False)['charge'])/(2*step)
        self.assertLess(abs(fd-analytic)/max(1,abs(analytic)),1e-9)

    def test_nonunit_topology_input_is_rejected(self):
        engine=self.engine()
        with self.assertRaises(ValueError):
            HopfInvariant(engine).evaluate(np.ones((*engine.grid.shape,3)))


if __name__=='__main__':
    unittest.main()
