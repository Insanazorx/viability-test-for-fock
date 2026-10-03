"""Validate and explicitly freeze predeclared configurations by exact bytes."""
from __future__ import annotations

import argparse
import hashlib
import sys

from common import ROOT, decode_data, inside, read_data, sha256, write_data

CONFIGS = {
    ("G0A-T01", "MACM6"): ("config/benchmark/g0a_t01.json.yaml", "validate_repository"),
    ("G0A-T02", "MACM6"): ("config/benchmark/g0a_t02_macm6.json.yaml", "validate_math_core"),
    ("G0A-T02", "RTX5070"): ("config/benchmark/g0a_t02_rtx5070.json.yaml", "validate_math_core_cuda"),
    ("G0A-T03", "MACM6"): ("config/benchmark/g0a_t03_macm6.json.yaml", "validate_run_discipline"),
    ("G0B-T01", "MACM6"): ("config/benchmark/g0b_t01_macm6.json.yaml", "validate_spectral_cpu"),
    ("G0B-T01", "RTX5070"): ("config/benchmark/g0b_t01_rtx5070.json.yaml", "validate_spectral_cuda"),
    ("G0B-T02", "MACM6"): ("config/benchmark/g0b_t02_macm6.json.yaml", "validate_hopf_cpu"),
    ("G0B-T02", "RTX5070"): ("config/benchmark/g0b_t02_rtx5070.json.yaml", "validate_hopf_cuda"),
    ("G0B-T03", "RTX5070"): ("config/benchmark/g0b_t03_rtx5070.json.yaml", "reproduce_stationary_cuda"),
    ("G4A-T01", "MACM6"): ("config/gate4/g4a_t01_macm6.json.yaml", "validate_operator_basis"),
    ("G0B-T05", "MACM6"): ("config/benchmark/g0b_t05_macm6.json.yaml", "validate_solver_preparation"),
    ("G0A-T04", "MACM6"): ("config/benchmark/g0a_t04_macm6.json.yaml", "validate_transfer"),
    ("G4C-T02", "MACM6"): ("config/gate4/g4c_t02_macm6.json.yaml", "validate_naturalness"),
    ("G4D-T04", "MACM6"): ("config/gate4/g4d_t04_macm6.json.yaml", "validate_decay"),
    ("G4B-T01", "MACM6"): ("config/gate4/g4b_t01_macm6.json.yaml", "validate_radiative"),
    ("G4A-T02", "MACM6"): ("config/gate4/g4a_t02_macm6.json.yaml", "validate_classification"),
    ("G4A-T03", "MACM6"): ("config/gate4/g4a_t03_macm6.json.yaml", "validate_switching"),
    ("G1A-T04", "MACM6"): ("config/gate1/g1a_t04_macm6.json.yaml", "validate_full_static_preparation"),
}
MACM6_AUDITS = {
    'G0A-T04': ('analysis.validate_transfer','validate_transfer',{'integrity'}),
    'G4C-T02': ('analysis.naturalness_status','validate_naturalness',{'integrity'}),
    'G4D-T04': ('cosmology.vacuum_decay','validate_decay',{'source_action','source_center','action_convergence','virial','tail','gravity_constraint_derivative','false_vacuum_radius','false_vacuum_action'}),
    'G4B-T01': ('analysis.radiative','validate_radiative',{'potential_gradient','potential_hessian','hessian_symmetry','vacuum_spectrum','scale_derivative','threshold_curvature','scalar_derivatives','lower_switch_counterterm'}),
    'G4A-T02': ('analysis.symmetry_audit', 'validate_classification', {'reflection'}),
    'G4A-T03': ('analysis.symmetry_audit', 'validate_switching', {'mu_series','xi_series'}),
}
REGISTRY = "config/frozen_registry.yaml"


def validate_config(config, root=ROOT):
    from jsonschema import Draft202012Validator
    schema = read_data(root / "config/schema.yaml")
    Draft202012Validator.check_schema(schema)
    violations = sorted(Draft202012Validator(schema).iter_errors(config), key=lambda e: str(e.path))
    if violations:
        raise ValueError("Invalid config: " + "; ".join(error.message for error in violations))
    record = CONFIGS.get((config["task"], config["machine"]))
    if not record or config["parameters"].get("handler") != record[1]:
        raise ValueError("No predeclared handler for this task/machine")
    if config["parameters"].get("allow_cloud") is not False:
        raise ValueError("These predeclared handlers do not permit cloud execution")
    if config["kind"] == "numerical" and config["precision"] == "N/A":
        raise ValueError("Numerical runs require an explicit precision")
    if not isinstance(config["parameters"].get("minimum_tests"), int) or isinstance(config["parameters"]["minimum_tests"], bool) or config["parameters"]["minimum_tests"] <= 0:
        raise ValueError("A positive minimum test count is required")
    if config["task"] == "G0A-T02":
        if config["precision"] != "float64" or config["kind"] != "numerical":
            raise ValueError("The core acceptance configs require float64 numerics")
        expected_tolerances = ({"identity_normalized", "rotation_normalized", "gradient_normalized", "reduction_normalized"}
                               if config["machine"] == "MACM6" else {"backend_normalized", "autograd_normalized"})
        if set(config["tolerances"]) != expected_tolerances:
            raise ValueError("Required core tolerances are absent")
        for key in ("samples_per_seed", "rotations_per_seed"):
            if key in config["parameters"] and (type(config["parameters"][key]) is not int or config["parameters"][key] <= 0):
                raise ValueError("Sample/rotation counts must be positive integers")
    elif config['task']=='G0B-T01':
        if config['kind']!='numerical' or config['precision']!='float64' or config['grid'] is None or config['box'] is None:
            raise ValueError('Spectral acceptance requires a float64 grid/box')
        required={'bandlimited_derivative','analytic_energy','parseval','skew_adjoint','vacuum_energy',
                  'unit_error','directional_gradient','symmetry_energy','smooth_derivative_final',
                  'centered_fd_final','vacuum_face','vacuum_face_gradient','nyquist_derivative'}
        if config['machine']=='RTX5070':
            required |= {'backend','autograd'}
        if set(config['tolerances']) != required:
            raise ValueError('Spectral acceptance tolerances missing')
        parameters=config['parameters']
        sequence=parameters.get('resolution_sequence',[])
        if len(sequence)<3 or any(type(n) is not int or n<9 for n in sequence) or sorted(set(sequence))!=sequence:
            raise ValueError('Increasing spectral resolution sequence required')
        if config['machine']=='MACM6' and (max(sequence)>33 or max(config['grid'])>33):
            raise ValueError('MACM6 acceptance is restricted to small grids <=33')
        even=parameters.get('even_grid',[])
        if len(even)!=3 or any(type(n) is not int or n<4 or n%2 or n>33 for n in even):
            raise ValueError('Small even grid required for the Nyquist audit')
        steps=parameters.get('gradient_steps',[])
        if len(steps)<3 or any(type(v) not in (int,float) or v<=0 for v in steps) or sorted(set(steps),reverse=True)!=steps:
            raise ValueError('Decreasing gradient difference steps required')
        if type(parameters.get('minimum_spectral_improvement')) not in (int,float) or parameters['minimum_spectral_improvement']<1:
            raise ValueError('Spectral convergence improvement must be explicit')
    elif config['task']=='G0B-T02':
        if config['kind']!='numerical' or config['precision']!='float64' or config['grid'] is None or config['box'] is None:
            raise ValueError('Hopf acceptance requires an explicit float64 grid/box')
        required={'unit_error','boundary_error','gauge_relative','fourier_difference','analytic_density_identity',
                  'helical_inverse','reflection_sign','antipodal_invariance','trivial_charge','gradient_directional',
                  'continuum_degree_error','unit_charge','charge_refinement','analytic_charge','smooth_deformation',
                  'deformation_drift','curl_relative','divergence_relative','harmonic_fraction'}
        if config['machine']=='RTX5070':
            required |= {'backend','autograd'}
        if set(config['tolerances'])!=required:
            raise ValueError('Hopf acceptance tolerances missing')
        p=config['parameters'];sequence=p.get('resolution_sequence',[])
        if len(sequence)<3 or any(type(n) is not int or n<9 or n%2!=1 or n>49 for n in sequence) or sorted(set(sequence))!=sequence:
            raise ValueError('Increasing small odd Hopf grids <=49 required')
        for key in ('half_box','profile_scale','profile_radius','deformation_amplitude','minimum_charge_improvement'):
            if type(p.get(key)) not in (int,float) or p[key]<=0:
                raise ValueError('Explicit positive Hopf profile/validation parameters required')
        if p['profile_radius']>=p['half_box']:
            raise ValueError('Compact map support must be inside every boundary')
        if config['grid']!=[sequence[-1]]*3:
            raise ValueError('Nominal Hopf grid must equal the final reference grid')
        period=sequence[-1]*2*p['half_box']/(sequence[-1]-1)
        if any(abs(length-period)>1e-12 for length in config['box']):
            raise ValueError('Paper endpoint grid needs FFT period N h, not 2L')
        amplitudes=p.get('coordinate_deformation',[])
        if len(amplitudes)!=3 or any(type(a) not in (int,float) or abs(a)*3.141592653589793/p['half_box']>=1 for a in amplitudes):
            raise ValueError('Coordinate deformation must preserve orientation')
        steps=p.get('gradient_steps',[])
        if len(steps)<3 or any(type(v) not in (int,float) or v<=0 for v in steps) or sorted(set(steps),reverse=True)!=steps:
            raise ValueError('Three decreasing charge-gradient difference steps required')
    elif config['task']=='G0B-T03':
        if config['machine']!='RTX5070' or config['kind']!='numerical' or config['precision']!='float64':
            raise ValueError('Stationary production requires RTX5070 float64')
        p=config['parameters']
        if [(row['size'],row['half_box'],row['energy']) for row in p.get('sequence',[])] != [
                (17,4.,281.3653),(21,4.,281.2711),(25,4.,281.2625),(33,8.,274.5448)]:
            raise ValueError('Matched source Table 2 sequence is immutable')
        if p.get('solver') != {'penalty':20000.,'outer_updates':4,'maxiter':120,'maxfun':180,
                              'gtol':1e-10,'ftol':1e-14,'history_size':100}:
            raise ValueError('Source AL/optimizer settings are immutable')
        expected={'energy_relative':5e-4,'unit_charge':5e-4,'constrained_rms':1e-5,
                  'unit_error':2e-15,'boundary_error':1e-14,'backend':5e-11,'autograd':5e-10,'resume':5e-12}
        if config['tolerances']!=expected or p.get('target_charge')!=-1.:
            raise ValueError('Predeclared stationary tolerances/charge changed')
        if config['grid']!=[33]*3 or config['box']!=[16.5]*3 or not p.get('stop_on_failed_grid'):
            raise ValueError('Exact source nominal grid and early failure stop required')
        if p.get('profile_scale')!=1.2 or p.get('profile_radius')!=3.4 or not p.get('contract_doc'):
            raise ValueError('Explicit independent initializer and contract required')
    elif config['task']=='G4A-T01':
        if config['kind']!='numerical' or config['precision']!='float64':
            raise ValueError('Operator witnesses require float64 numerics with exact rational enumeration')
        if any(config[k] is not None for k in ('grid','box','time_step','optimizer','integrator')):
            raise ValueError('This analytic operator audit has no lattice or evolution')
        if config['parameters'].get('max_canonical_dimension')!=4 or config['parameters'].get('quotient')!='IBP only':
            raise ValueError('G4A-T01 acceptance scope is d<=4 modulo IBP only')
        if type(config['parameters'].get('samples_per_seed')) is not int or config['parameters']['samples_per_seed']<20:
            raise ValueError('At least twenty operator witnesses per seed required')
        if set(config['tolerances'])!={'so4_normalized','chi_parity'}:
            raise ValueError('Frozen SO4/parity tolerances required')
    elif config['task']=='G0B-T05':
        if config['kind']!='numerical' or config['precision']!='float64' or config['machine']!='MACM6':
            raise ValueError('Solver preparation is an identified MACM6 float64 reference')
        p=config['parameters']
        if p.get('oracle_grid') not in (5,7) or p.get('smoke_grid') not in (7,9):
            raise ValueError('Solver preparation is restricted to explicitly small grids')
        required={'direct_energy','direct_charge','direct_directional','hvp_difference','hvp_symmetry',
                  'chart_gradient','projected_symmetry','charge_projection','retracted_hvp','smoke_residual',
                  'smoke_energy_fraction','unit_error','boundary_error','multiplier_update'}
        if set(config['tolerances'])!=required:
            raise ValueError('All solver/reference tolerances must be frozen')
        if not p.get('contract_doc') or not p.get('objective') or not p.get('acceptance'):
            raise ValueError('Preparation scope and acceptance contract required')
    elif config['task']=='G1A-T04':
        if config['machine']!='MACM6' or config['kind']!='numerical' or config['precision']!='float64' or config['grid']!=[5,5,5]:
            raise ValueError('Full-M preparation is a restricted 5^3 MACM6 reference')
        if set(config['tolerances'])!={'gradient','hvp_difference','hvp_symmetry','so4_energy','heavy_reduction','fock_potential','normal_masses'}:
            raise ValueError('Full-M preparation tolerances must be explicit')
        if set(config['parameters'].get('coefficients',{}))!={'z_m','alpha','mu','sigma0','zeta'}:
            raise ValueError('Only stated baseline static coefficients allowed')
    elif config['task'] in MACM6_AUDITS:
        expected_kind,expected_precision=('control','N/A') if config['task']=='G0A-T04' else ('numerical','float64')
        if config['machine']!='MACM6' or config['kind']!=expected_kind or config['precision']!=expected_precision or config['grid'] is not None:
            raise ValueError('Analytic MACM6 audit requires explicit float64 and no lattice')
        if set(config['tolerances'])!=MACM6_AUDITS[config['task']][2]:
            raise ValueError('All audit tolerances must be frozen')
        if not all(config['parameters'].get(k) for k in ('contract_doc','objective','method','acceptance','convergence','claim_scope','next_action')):
            raise ValueError('Audit scope and report contract required')
    elif config["kind"] != "control" or config["precision"] != "N/A":
        raise ValueError("Infrastructure handlers require control/N/A")
    return record


def freeze_configs(root=ROOT):
    entries = {}
    for (task, machine), (relative, handler) in CONFIGS.items():
        path = inside(root, relative, "config")
        config = read_data(path)
        validate_config(config, root)
        entries[f"{task}/{machine}"] = {"path": relative, "handler": handler, "sha256": sha256(path)}
    registry = {"schema_version": 1, "entries": entries,
                "policy": "Exact byte hashes; changed configs require explicit freeze and commit before acceptance runs"}
    write_data(root / REGISTRY, registry)
    return registry


def load_config(path, root=ROOT):
    raw = path.read_bytes()
    config = decode_data(raw)
    record = validate_config(config, root)
    relative = path.resolve().relative_to(root.resolve()).as_posix()
    if relative != record[0]:
        raise ValueError("Use the canonical predeclared config path")
    registry = read_data(root / REGISTRY)
    entry = registry["entries"].get(f"{config['task']}/{config['machine']}")
    digest = hashlib.sha256(raw).hexdigest()
    if not entry or entry["path"] != relative or entry["handler"] != record[1] or entry["sha256"] != digest:
        raise ValueError("Frozen config changed; review, explicitly freeze and commit before running")
    return config, raw, digest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("freeze", "check"))
    args = parser.parse_args()
    try:
        if args.action == "freeze":
            result = freeze_configs()
            print(f"Explicitly froze {len(result['entries'])} configs. Commit registry/configs before acceptance runs.")
        else:
            for relative, _ in CONFIGS.values():
                load_config(ROOT / relative)
            print("All frozen config hashes match.")
    except (ValueError, KeyError, OSError) as error:
        print(f"configuration: {error}", file=sys.stderr)
        raise SystemExit(1)
