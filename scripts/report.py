"""Create one evidence-backed report for a predeclared setup/core substep."""
from __future__ import annotations

import argparse
import json
import sys

from common import ROOT, inside, read_data, sha256
from provenance import verify_run
from configuration import MACM6_AUDITS


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    run = inside(ROOT, f"runs/{args.run_id}", "runs")
    metadata, result = read_data(run / "metadata.json"), read_data(run / "result.json")
    if metadata["run_id"] != args.run_id or result["run_id"] != args.run_id:
        raise ValueError("Run ID does not match evidence")
    if metadata["task"] not in set(MACM6_AUDITS) | {"G0A-T01", "G0A-T02", "G0A-T03",'G0B-T01','G0B-T02','G4A-T01','G0B-T05','G1A-T04'}:
        raise ValueError("Automatic report prose is implemented only for the setup/core tasks")
    if sha256(run / "config.yaml") != metadata["config_sha256"]:
        raise ValueError("Config snapshot was changed")
    if result["status"] not in {"PASS", "FAIL", "BLOCKED"}:
        raise ValueError("Unsupported result status")
    metrics = result["metrics"]
    seal_hash = verify_run(run) if metadata.get("integrity_schema_version") or (run/"integrity.json").exists() else None
    artifacts = []
    for name in ("config.yaml", "metadata.json", "result.json", "validation.log", "environment.json", "integrity.json"):
        path = run / name
        if path.is_file():
            artifacts.append(f"- `{path.relative_to(ROOT).as_posix()}` — SHA256 `{sha256(path)}`")
    if result.get('checkpoint_sha256'):
        path=inside(ROOT,result['checkpoint_path'],'checkpoints')
        if sha256(path)!=result['checkpoint_sha256']:
            raise ValueError('Checkpoint hash does not match sealed result')
        artifacts.append(f"- `{result['checkpoint_path']}` — SHA256 `{result['checkpoint_sha256']}` (ignored HDF5 initial field; not a stationary solution)")
    anomalies = [f"Dirty Git tree at run start: {metadata['uncommitted_diff']}.",
                 "Python 3.12.14 control environment exists; numerical dependencies are not yet installed/frozen.",
                 "No Git remote or remote runner is configured. CLOUD remains paused.",
                 "Hardware model/RAM capacity was not measured; MACM6 denotes the assigned control responsibility."]
    if not metrics.get("publication_present"):
        anomalies.append("`yayınlanan.pdf` is absent. This does not fail G0A-T01, but G0A-T02 cannot start without it.")
    if result.get("anomaly"):
        anomalies.append(result["anomaly"])
    values = {
        "task": metadata["task"], "machine": metadata["machine"], "status": result["status"],
        "git_commit": metadata["git_commit"], "config_sha256": metadata["config_sha256"],
        "run_id": args.run_id, "started_utc": metadata["started_utc"],
        "finished_utc": result["finished_utc"], "wall_time": f"{result['wall_time_seconds']:.6f} seconds",
        "peak_ram_gb": f"{result['peak_ram_gb']:.6f} ({result['peak_ram_method']})",
        "peak_vram_gb": "N/A — no GPU execution" if result["peak_vram_gb"] is None else str(result["peak_vram_gb"]), "precision": metadata["precision"],
        "objective": "Complete G0A-T01: committed repository skeleton, canonical state, config schema and report template on MACM6.",
        "inputs": f"AGENTS.md §§3–7, G0A-T01 and §17; config `{metadata['config_path']}`. No publication contents are required for this setup substep.",
        "method": "Engineering validation only: Python standard-library control plane, complete path inventory, automated control-plane tests and Git provenance capture. No numerical physics calculation was performed.",
        "tolerances": "Every required path exists; state validation succeeds; all control tests exit successfully; CLOUD is paused. No physics tolerance is relaxed or evaluated.",
        "metrics": "```json\n" + json.dumps(metrics, indent=2, ensure_ascii=False) + "\n```",
        "convergence": "Not applicable to a repository setup. Regression checks cover machine-order enforcement, N/A rendering, dependency rejection, report/config evidence and generated views.",
        "evaluation": f"{result['status']} for G0A-T01 infrastructure only. Direct dependency pins and a Python 3.12 environment are present; full numerical dependency locking and run/seed discipline remain G0A-T03. No scientific gate has passed.",
        "anomalies": "\n".join(f"- {line}" for line in anomalies),
        "artifacts": "\n".join(artifacts) + "\nNo checkpoint or large numerical array was produced. Source/config code is identified by the Git commit above.",
        "reproduction": f"```sh\npython3.12 -m venv .venv\n.venv/bin/python -m unittest discover -s tests/unit -v\n.venv/bin/python scripts/ctl.py validate\n```\nFor an identified re-run, use an isolated checkout of `{metadata['git_commit']}` (where G0A-T01 is RUNNING), then `.venv/bin/python scripts/run.py --config {metadata['config_path']}`. A completed task is not silently reopened.",
        "changes": "First setup report; no previous report or physics implementation exists.",
        "next_action": "G0A-T02 on MACM6: restore/hash the exact `yayınlanan.pdf`, then derive Appendix A core definitions and their reference checks. Device switching waits for the committed mathematical core.",
        "handoff": "NEXT.md, MACHINE_HANDOFF.md, AGENTS.md#g0a; no transfer to RTX5070 or CLOUD yet.",
    }
    if metadata["task"] == "G0A-T02":
        config = read_data(run / "config.yaml")
        cuda = metadata["machine"] == "RTX5070"
        input_lines = [f"- `{path}` — SHA256 `{digest}`" for path,digest in metadata["input_sha256"].items()]
        followup = ("G0A-T03 on MACM6: complete numerical environment/run discipline after both required machine reports pass."
                    if cuda else "G0A-T02 on RTX5070: validate the float64 CUDA mirror against the CPU reference and analytic gradients. Do not mark the entire task PASS before this report exists.")
        core_metrics = metrics.get("math_core", {})
        convergence = ("CUDA float64 outputs and autograd directional products are compared with NumPy/independent analytic contractions. This is an algebra/backend check, not a continuum or soliton test."
                       if cuda else "Three independent seeds, an amplitude range 1e-3 to 1e3, proper rotations and an orientation-reversing reflection. Central finite-difference steps 1e-3, 1e-4 and 1e-5 are recorded per seed; the smallest step is checked against the frozen gradient tolerance. No grid/volume convergence or Hopf quantization is claimed.")
        values.update({
            "objective": f"Complete the {metadata['machine']} responsibility for G0A-T02: source-derived mathematical core definitions, invariant/rotation identities and {'CUDA/autograd mirror checks' if cuda else 'independent CPU finite-difference checks'}.",
            "inputs": "User-supplied publication, verified DOI 10.1016/j.nuclphysb.2026.117639; PDF pp. 2-5, 8, 17-18; Eqs. 4-10, 15-19, 20, 30-31, 64-68, A.1-A.3. Exact input identities:\n" + "\n".join(input_lines),
            "method": "Predeclared channels-last six-component field representation; isometric dual triplets; full static algebraic densities and the distinct dimensionless reduced Eq. 65 coefficients; uniform-cell Eq. 68 helicity integral supplied with A and B. "
                      + ("Actual CUDA tensors/autograd compared with CPU float64." if cuda else "NumPy float64; independent Levi-Civita/matrix contractions and analytic directional derivatives compared with central differences.")
                      + " Pointwise sampled data only; no spatial derivative/inversion solver or minimization has been implemented.",
            "tolerances": "Frozen before the reported run:\n```json\n"+json.dumps(config["tolerances"],indent=2)+"\n```\nIdentity/rotation/reduction residuals divide by max(1, the relevant invariant/magnitude scale); directional checks divide by max(1, abs(analytic derivative)). Scale-aware residuals are defined in src/analysis/validate_core.py.",
            "convergence": convergence,
            "evaluation": f"{result['status']} for the {metadata['machine']} responsibility only. All listed numeric thresholds, the minimum test count and source/config identity must pass. Worst errors: "
                          + json.dumps(core_metrics.get("worst_errors", {}))
                          + (". MACM6 and RTX5070 reports must both exist to complete G0A-T02." if cuda else ". CUDA has not been executed here; the task remains RUNNING after MACM6 is marked done. This does not establish a soliton, spectrum, relic abundance or cosmological viability."),
            "anomalies": f"- Dirty Git tree at run start: {metadata['uncommitted_diff']}.\n"
                         "- The exact supplied PDF is an external ignored input; copy it to RTX5070 with the recorded SHA256.\n"
                         "- NumPy-only MACM6 core environment is frozen; full CPU/CUDA environment policy remains G0A-T03.\n"
                         "- Source text extraction required visual confirmation of fractions/signs.\n"
                         "- Fourier inversion/initial-map orientation remain G0B; no unit Hopf charge is reported.\n"
                         + (f"- {result['anomaly']}\n" if result.get("anomaly") else ""),
            "artifacts": "\n".join(artifacts)+"\nNo checkpoint/large numerical field was produced. Backend implementation and math contract are identified by the Git commit above.",
            "reproduction": f"```sh\n.venv/bin/python scripts/run.py --config {metadata['config_path']}\n.venv/bin/python scripts/report.py --run-id EXACT_NEW_RUN_ID\n```\nUse an isolated checkout of `{metadata['git_commit']}` with the matching source PDF and frozen package versions from environment.json. The assigned machine must be unfinished/RUNNING; reruns never silently reopen completed responsibilities.",
            "changes": "First mathematical-core report. Compared with the setup report, the source identity, NumPy reference, backend-neutral formulas, CUDA mirror implementation and numeric acceptance checks are now present. Prior reports remain unchanged.",
            "next_action": followup,
            "handoff": "NEXT.md, MACHINE_HANDOFF.md, docs/MATH_CORE.md, docs/RTX5070_CORE_HANDOFF.md, config/benchmark/publication.source.yaml, and the exact machine-specific G0A-T02 config.",
        })
    if metadata["task"] == "G0A-T03":
        values.update({
            "objective":"Complete G0A-T03 on MACM6: typed config loading, exact frozen config hashes, immutable identified run evidence, environment versions and seed discipline.",
            "inputs":"AGENTS.md G0A-T03 and reproducibility §§4-7, user instruction to finish MACM6 infrastructure first. G0A-T01 is the passed prerequisite. G0A-T02 CUDA verification remains pending and is not waived.\n\n"
                     +"\n".join(f"- `{path}` — SHA256 `{digest}`" for path,digest in metadata['input_sha256'].items()),
            "method":"Safe YAML/JSON parsing rejects duplicate/non-finite values; Draft 2020-12 schema and a predeclared handler registry validate configs. Exact byte hashes are frozen before launch. Runs use UTC/commit/config-hash identities, exclusively created read-only snapshots, complete installed package capture and an integrity manifest. Python/NumPy seeds are explicit; CUDA policy is implemented but unexecuted on MACM6. Small SciPy ODE, HDF5 float64 roundtrip, Matplotlib Agg rendering and pip dependency checks validate the CPU environment. RAM is sampled from the parent and explicitly registered children. No model-physics calculation or remote execution is performed.",
            "tolerances":"All workflow checks must be true; every test must pass; every config/environment/artifact hash must match. Repeated same-seed fingerprints must match exactly; distinct declared seeds must differ. The elementary CPU-library ODE smoke error must be <1e-8; HDF5 values must round-trip exactly; PNG rendering/pip check must succeed. GPU completion flags must remain unchanged. Numeric model-physics tolerances are not modified.",
            "convergence":"Exact bookkeeping checks and deterministic seed repetitions, not grid/volume convergence. RAM is an observed sampled peak (10 ms cadence), not a guaranteed instantaneous aggregate maximum. Cross-device/Windows execution and CUDA reproducibility await their actual machines.",
            "evaluation":f"{result['status']} for the MACM6 G0A-T03 infrastructure responsibility. The CPU environment, config/run discipline and regression checks are evaluated in Primary metrics. This does not complete G0A-T02 or any G0B physics gate.",
            "anomalies":f"- Dirty Git tree at run start: {metadata['uncommitted_diff']}.\n- RTX5070 has no connected execution path from this session; CUDA remains unverified.\n- G0A-T03 was selected independently with a recorded reason and completed G0A-T01 prerequisite, at the user's request.\n- CLOUD remains paused and remote runners remain disabled.\n- Full MACM6 environment is frozen; PyTorch/CUDA build selection is still machine-specific.\n- Development checks exposed recursive-YAML exception handling and restricted host-process enumeration; both were corrected before the identified acceptance run. Profiling now queries only the current process and registered child PIDs.\n"+(f"- {result['anomaly']}\n" if result.get('anomaly') else ''),
            "artifacts":"\n".join(artifacts)+"\nNo physics checkpoint or large array was produced. Temporary integrity/seed fixtures are deleted after validation.",
            "reproduction":f"```sh\npython3.12 -m venv .venv\n.venv/bin/python -m pip install -r requirements/macm6.freeze.txt\n.venv/bin/python scripts/configuration.py check\n.venv/bin/python scripts/run.py --config {metadata['config_path']}\n```\nUse an isolated checkout of `{metadata['git_commit']}` where this task is RUNNING. The environment lock targets MACM6 macOS arm64; other machines require their own resolved environment. Completed responsibilities are not silently reopened.",
            "changes":"Completes the workflow foundation left pending by the math-core report. Adds safe/typed config validation, explicit frozen hashes, complete MACM6 package freeze, integrity checks, portable RAM measurement and single-action focus for independent work while a device is unavailable. Earlier physics definitions/acceptance tolerances and reports remain unchanged.",
            "next_action":"Return the single NEXT action to G0A-T02 on RTX5070: connect/open the matching checkout and execute the CUDA mirror with the exact supplied source PDF. Do not mark RTX5070 done without its own passing report.",
            "handoff":"MACHINE_HANDOFF.md, NEXT.md, docs/RUNBOOK.md, docs/RTX5070_CORE_HANDOFF.md, config/frozen_registry.yaml and config/benchmark/g0a_t02_rtx5070.json.yaml.",
        })
        if metadata.get("recovery"):
            values["changes"] += "\n\nExplicit recovery from the prior infrastructure failure:\n```json\n" + json.dumps(metadata["recovery"],indent=2) + "\n```"
            values["anomalies"] += "\n- The initial SciPy 1.15.3 PROPACK import failed on this macOS. Its report/evidence and old freeze are preserved; the corrected freeze uses SciPy 1.16.3. The observed loader error matches [SciPy issue #25635](https://github.com/scipy/scipy/issues/25635). No physics operator or tolerance was changed."
        if result["status"] != "PASS":
            values["next_action"] = "Resolve the recorded infrastructure anomaly, preserve this report/run, record an explicit recovery decision, then repeat G0A-T03 on MACM6. Do not record the environment as validated or advance to RTX5070 until acceptance passes."
    if metadata['task']=='G0B-T01':
        config=read_data(run/'config.yaml')
        cuda=metadata['machine']=='RTX5070'
        values.update({
            'objective':f"Complete the {metadata['machine']} G0B-T01 responsibility: full-grid FFT derivatives, Eq. (65) reduced energy and analytic discrete variations on small manufactured fields.",
            'inputs':'User-supplied publication, PDF p. 8, Eqs. (64)-(68), visually checked; docs/G0B_SPECTRAL.md fixes discretization and fixture definitions. The user explicitly deferred RTX5070 while requesting MACM6 preparation. Exact inputs:\n'+
                     '\n'.join(f'- `{path}` — SHA256 `{digest}`' for path,digest in metadata['input_sha256'].items())+
                     '\n\nPrerequisite responsibility scope:\n```json\n'+json.dumps(metadata['prerequisite_scope'],indent=2)+'\n```',
            'method':'Periodic anisotropic box; endpoint excluded, orthonormal full 3-D FFTs, D_i=FFT^-1(i k_i FFT). Real even-grid first-derivative Nyquist multiplier is zero and audited; no modes are filtered on odd grids. Eq. (65) uses both unchanged one-half factors and cell-volume quadrature. The analytic collocation energy gradient uses the skew-adjoint derivative; a separate centered finite-difference implementation checks second-order convergence. Constant vacuum, a localized smooth vacuum bump, finite Fourier modes, an analytic nonbandlimited scalar, rotations/translations and three seeded tangent variations are used. '+
                     ('Actual CUDA float64 tensors and FFT/autograd are compared with NumPy.' if cuda else 'NumPy float64 is the MACM6 independent reference. A shared Torch/CUDA implementation is present but unexecuted here.'),
            'tolerances':'Predeclared before the identified run:\n```json\n'+json.dumps(config['tolerances'],indent=2)+'\n```\nErrors compare max absolute differences normalized by max(1, max expected magnitude), except centered-FD relative L2 errors, raw vacuum/face/Nyquist errors and normalized skew-adjoint bilinear residuals. The final smooth spectral error and improvement >=1e4, centered-FD observed order in [1.8,2.2], final tangent gradient error and all tests must pass. This changes none of the published stationary-solver reproduction tolerances.',
            'convergence':'The 9^3,13^3,17^3,25^3,33^3 sequence tests analytic spectral derivatives and independent centered derivatives on a fixed anisotropic box. A separate 16^3 audit covers even-grid reality/skew-adjointness. Two-angle energies are analytically known. Tangent variations use steps 1e-3,1e-4,1e-5 and a unit-sphere retraction. This is fixture convergence; no soliton continuum/box convergence, minimization residual or physical Hessian is evaluated. RAM is a sampled parent+registered-child RSS peak.',
            'evaluation':f"{result['status']} for the {metadata['machine']} responsibility only. The checks and worst errors in Primary metrics decide acceptance. "+
                         ('CUDA and CPU responsibility reports are both required before the whole task passes.' if cuda else 'Whole G0B-T01 stays RUNNING because RTX5070 has not executed its mirror. G0A-T02 CUDA remains deferred/unverified. This is validated small-grid CPU preparation, not a passing G0B gate or dark-sector viability result.'),
            'anomalies':f"- Dirty Git tree at run start: {metadata['uncommitted_diff']}.\n- Source PDF is an ignored external input; its hash is checked before launch.\n- Periodic collocation nonlinear products can alias on unresolved data; manufactured-field convergence does not certify future soliton data.\n- A finite periodic boundary is not spatial infinity; the vacuum fixture controls seams but does not establish topology.\n- Real even-grid Nyquist modes have zero first derivative by explicit convention; they are not resolved physical modes.\n- User-authorized CPU prerequisite decomposition preserves every parent prerequisite and does not set any RTX5070 completion flag.\n- CLOUD stays paused with zero budget and remote runners disabled.\n"+(f"- {result['anomaly']}\n" if result.get('anomaly') else ''),
            'artifacts':'\n'.join(artifacts)+'\nOnly scalar fixture metrics and logs are saved. No stationary field, checkpoint, large array, Hopf charge or eigenvalue is produced.',
            'reproduction':f"```sh\npython3.12 -m venv .venv\n.venv/bin/python -m pip install -r requirements/{'macm6.txt' if cuda else 'macm6.freeze.txt'}\n.venv/bin/python scripts/configuration.py check\n.venv/bin/python scripts/run.py --config {metadata['config_path']}\n.venv/bin/python scripts/report.py --run-id EXACT_NEW_RUN_ID\n```\nUse an isolated checkout of `{metadata['git_commit']}` where this machine responsibility is RUNNING/unfinished and the source PDF has the exact hash. "+('Install/freeze the actual CUDA-enabled PyTorch build using the RTX5070 core handoff first.' if cuda else 'The frozen environment targets MACM6 macOS arm64; there is no MPS or GPU acceptance here.'),
            'changes':'First G0B-T01 report. Extends the pointwise mathematical core to an explicit periodic spatial discretization, Eq. (65) integrated energy, its analytic node gradient and independent CPU reference checks. Records machine-scoped prerequisites and the explicit RTX5070 deferral; earlier core/source definitions and reports remain unchanged.',
            'next_action':'G0B-T02 on MACM6: implement/validate Coulomb-gauge Fourier inversion, the source initial map and Hopf sign. RTX5070 remains deferred until the user requests continuation, starting with G0A-T02 CUDA.' if result['status']=='PASS' and not cuda else ('Continue the prerequisite-defined registry after both G0B-T01 reports pass.' if result['status']=='PASS' else 'Classify the recorded failure and run the smallest discriminating check before repeating or widening this substep.'),
            'handoff':'NEXT.md, MACHINE_HANDOFF.md, AGENTS.md#g0b, docs/G0B_SPECTRAL.md and the exact machine-specific G0B-T01 config. The source PDF must be copied separately with its recorded SHA256.',
        })
    if metadata['task']=='G0B-T02':
        config=read_data(run/'config.yaml');cuda=metadata['machine']=='RTX5070'
        values.update({
            'objective':f"Complete {metadata['machine']} G0B-T02: Coulomb Fourier inversion, the paper's Q_H=-1 convention and small-grid unit/trivial/deformed-map topology validation.",
            'inputs':'Supplied publication, PDF pp. 8-9, Eqs. (67)-(68) and section 7.1; docs/G0B_HOPF.md derives the independent compact initializer and sign. Every exact input:\n'+
                     '\n'.join(f'- `{path}` — SHA256 `{digest}`' for path,digest in metadata['input_sha256'].items())+
                     '\n\nPrerequisite scope:\n```json\n'+json.dumps(metadata['prerequisite_scope'],indent=2)+'\n```',
            'method':'Paper endpoint-included grid with h=2L/(N-1), FFT period N h and fixed south-pole boundary. Full-grid odd FFT derivatives generate F and B. Ahat=i(k x Bhat)/k^2 for nonzero k, harmonic Ahat=0. Physical and Fourier helicities are compared; divergence, gauge, curl reconstruction and harmonic flux are diagnosed using the original B. An independent compact quaternion Hopf map with analytically known radial degree -1, analytic Berry potential and exact profile derivatives fixes orientation/normalization. Seeded tangent and positive-Jacobian coordinate homotopies, spatial/target reflections, trivial/vacuum maps and analytic discrete charge-gradient finite differences provide independent checks. '+
                     ('Actual CUDA FFT/autograd and CPU comparisons are performed.' if cuda else 'NumPy/SciPy float64 on MACM6; CUDA operations are implemented but unexecuted here.'),
            'tolerances':'Frozen before this run:\n```json\n'+json.dumps(config['tolerances'],indent=2)+'\n```\nFinal unit/deformed charge errors and the last-two-grid charge difference must each be <=5e-4; charge-error improvement must be >=10. Closure uses relative discrete L2 norms with k_box=2pi/min(periods) for divergence normalization. Other algebraic/sign/gradient checks use their declared absolute or max(1, expected magnitude) normalization. Coarse-grid closure is recorded but does not certify coarse topology. No charge is normalized to its target.',
            'convergence':'17^3,25^3,33^3,49^3 at physical half-box L=4; spacing and effective FFT period are recorded per row. Analytic Berry helicity and quaternion winding quadratures form independent continuum references. Three seeded tangent deformations and one orientation-preserving coordinate deformation are evaluated on the finest grid. Off-S2 central differences use steps 1e-3,1e-4,1e-5. This concerns a known analytic map, not a stationary solution or published minimizer table.',
            'evaluation':f"{result['status']} for the {metadata['machine']} responsibility only. Primary metrics include all threshold decisions, charge convergence and independent references. "+
                         ('Whole G0B-T02 additionally requires its passing MACM6 report.' if cuda else 'Whole G0B-T02 remains RUNNING until RTX5070 passes. G0A-T02/G0B-T01 CUDA also remain deferred; no stationary energy, physical stability or viability claim follows.'),
            'anomalies':f"- Dirty Git tree at run start: {metadata['uncommitted_diff']}.\n- The PDF specifies a unit compactified map but omits its explicit profile/scale; no accompanying archive is present in this workspace. The independently derived fixture reproduces the sector/sign, not an archived initializer or stationary checkpoint.\n- The source endpoint-included convention is added explicitly; earlier G0B-T01 manufactured fixtures/configs remain unchanged.\n- Finite-grid F/B can alias and fail closure; the raw diagnostics and refinement are mandatory.\n- The 49^3 MACM6 calculation is a small reference evaluation of a known map, not a production minimization campaign.\n- RTX5070 remains explicitly deferred; CLOUD is paused with zero budget.\n"+(f"- {result['anomaly']}\n" if result.get('anomaly') else ''),
            'artifacts':'\n'.join(artifacts)+'\nThe HDF5 artifact is the independently generated initial field, stationary=false. It is ignored by Git and must be separately copied with its hash or regenerated from the exact config/code. Large arrays are not added to Git.',
            'reproduction':f"```sh\npython3.12 -m venv .venv\n.venv/bin/python -m pip install -r requirements/{'macm6.txt' if cuda else 'macm6.freeze.txt'}\n.venv/bin/python scripts/configuration.py check\n.venv/bin/python scripts/run.py --config {metadata['config_path']}\n.venv/bin/python scripts/report.py --run-id EXACT_NEW_RUN_ID\n```\nUse an isolated checkout of `{metadata['git_commit']}` where this responsibility is RUNNING/unfinished, with the source PDF matching its SHA256. CUDA execution additionally requires a frozen driver-compatible PyTorch build and completed preceding GPU reports.",
            'changes':'First G0B-T02 report. Adds paper-grid origin/period support, raw Coulomb inversion and closure/flux diagnostics, independent compact Hopf/sign references, a checked analytic discrete charge gradient and a hashed initial-field HDF5 artifact. Earlier source/core acceptance configs and scientific gate flags remain intact.',
            'next_action':'Preserve the verified initial field and CPU report. G0B-T03 stationary minimization is assigned to RTX5070 first, which remains deferred at the user request; resume first at G0A-T02 CUDA only when requested.' if result['status']=='PASS' else 'Classify the failed diagnostic and perform the smallest discriminating refinement/implementation check before repeating this fixture; do not loosen the unit-charge threshold or claim a physical failure prematurely.',
            'handoff':'MACHINE_HANDOFF.md, NEXT.md, AGENTS.md#g0b, docs/G0B_HOPF.md, exact G0B-T02 config and the reported HDF5 path/hash. Original-paper stationary reproduction remains G0B-T03.',
        })
    if metadata['task']=='G4A-T01':
        config=read_data(run/'config.yaml');operators=metrics.get('operator_basis',{})
        table='| ID | Bulk operator | Dimension | Sector |\n|---|---|---:|---|\n'+''.join(
            f"| {row['id']} | `{row['expression']}` | {row['dimension']} | {row['sector']} |\n"
            for row in operators.get('catalog',[]))
        summary={key:value for key,value in operators.items() if key!='catalog'}
        values.update({
            'objective':'Complete G4A-T01 on MACM6: a chosen-order d<=4 analytic dark/metric bulk operator basis, with source higher-order exceptions and an explicit interface for unspecified matter.',
            'inputs':'AGENTS.md#g4a; supplied PDF pp. 2-5 and 13, Eqs. (4)-(8),(20)-(24),(30) and Radiative status. Exact inputs:\n'+
                     '\n'.join(f'- `{path}` — SHA256 `{digest}`' for path,digest in metadata['input_sha256'].items()),
            'method':'Analytic SO(4) invariant-ring and Lorentz/diffeomorphism index counting, modulo integration by parts only. Scalar monomials generated with weights (1,1,2,2) for (lambda,chi,C1,C2), even chi powers. Independent Hilbert-series coefficients and exact rational evaluation rank on physical canonical M12/M34 states check the twenty potential monomials. Seeded NumPy float64 proper rotations check potential and both M kinetic channels; improper internal reflections witness the extra symmetry that must not be assumed. No lattice, optimizer, loop integral or added model term is used.',
            'tolerances':'Frozen numeric witness tolerances:\n```json\n'+json.dumps(config['tolerances'],indent=2)+'\n```\nCounts, dimensions and exact rational rank require exact equality; all 32 bulk IDs must be unique. Relative rotation error divides by max(1, abs(expected)). Scope is fixed before acceptance, not widened after a failure.',
            'metrics':table+'\n```json\n'+json.dumps(summary,indent=2)+'\n```\nFull machine-readable catalog and all checks are sealed in result.json. Unit tests: '+str(metrics.get('tests_run',0))+'.',
            'convergence':'No continuum or runtime scan applies to an exact operator enumeration. The generating-series coefficients [1,1,4,4,10] independently match the potential count. Exact rank is twenty using '+str(operators.get('exact_integer_samples',0))+' canonical integer field samples. Three independent seeds probe continuous proper rotations and chi parity; the tests exercise omitted Pfaffian, tadpole, curvature and kinetic channels.',
            'evaluation':result['status']+' for this declared operator-enumeration substep only. G4A-T02/T03 classification and functional audits, G4B loops/matching and G4C naturalness decision remain unfinished. G0A-T02/G0B CUDA prerequisites stay RUNNING/deferred. This is not a radiative naturalness, vacuum lifetime or full viability pass.',
            'anomalies':f"- Dirty Git tree at run start: {metadata['uncommitted_diff']}.\n- The invariant ring and d<=4 scope are independently derived, not a quoted complete basis from the source.\n- L_m is not specified in the paper: only formal scalar-singlet matter decorations are supplied; a concrete visible-sector and indexed matter operator basis awaits a matter definition.\n- Higher-order L4, mu, Xi and portal entries are source exceptions; no complete d=6/8/10 basis is claimed.\n- Topological/boundary terms are recorded separately; their global effects are not set to zero for G4D instantons.\n- No loop coefficient, cutoff choice or tuning estimate has been computed.\n- RTX5070 remains deferred; CLOUD paused and budget zero.\n"+(f"- {result['anomaly']}\n" if result.get('anomaly') else ''),
            'artifacts':'\n'.join(artifacts)+'\nThe small operator catalog is part of the sealed result.json. No numerical field/checkpoint or new EFT coefficient was produced. The source PDF is an external ignored input with the hash above.',
            'reproduction':f"```sh\npython3.12 -m venv .venv\n.venv/bin/python -m pip install -r requirements/macm6.freeze.txt\n.venv/bin/python scripts/configuration.py check\n.venv/bin/python scripts/run.py --config {metadata['config_path']}\n.venv/bin/python scripts/report.py --run-id EXACT_NEW_RUN_ID\n```\nUse an isolated checkout of `{metadata['git_commit']}` where G4A-T01 is RUNNING/unfinished, with the matching source PDF. Reproduction does not resume a deferred GPU or reopen a completed task silently.",
            'changes':('Recovery from the preserved implementation failure: '+metadata['recovery']['cause']+' Repair: '+metadata['recovery']['change']+' Operator definitions, source, config hash and tolerances are unchanged; the previous FAIL report is an exact hashed input.' if metadata.get('recovery') else 'First G4A-T01 report. Opens the AGENTS-authorized parallel MACM6 theory track after CPU foundations, while retaining all unfinished CUDA gates. Adds an exact chosen-order basis and machine-readable audit inputs without changing the baseline action.'),
            'next_action':'G4A-T02 on MACM6: classify absent allowed terms, IBP/EOM redundancies and genuinely symmetry-forbidden terms. Then G4A-T03 audits lower-order lambda^n C2^2 and the Xi functional coefficients before G4B loop matching.' if result['status']=='PASS' else 'Classify the failed exact count/rank or invariant witness; correct the smallest implementation/analytic issue before repeating.',
            'handoff':'NEXT.md, MACHINE_HANDOFF.md, AGENTS.md#g4a, docs/G4A_OPERATOR_BASIS.md and this sealed catalog; GPU queue is unchanged.',
        })
    if metadata['task'] in set(MACM6_AUDITS) | {'G0B-T05','G1A-T04'}:
        config=read_data(run/'config.yaml');p=config['parameters']
        values.update({
            'objective':p['objective'],
            'inputs':'Source PDF '+p.get('source_sections','section 7.1 Eqs. (70)-(73)')+', plus the mathematical/engineering contract '+p['contract_doc']+' and the passed CPU references. Exact inputs:\n'+
                     '\n'.join(f'- `{path}` — SHA256 `{digest}`' for path,digest in metadata['input_sha256'].items()),
            'method':p['method'],
            'tolerances':'Frozen before acceptance:\n```json\n'+json.dumps(config['tolerances'],indent=2)+'\n```\n'+p['acceptance'],
            'metrics':'```json\n'+json.dumps(metrics,indent=2)+'\n```',
            'convergence':p['convergence'],
            'evaluation':result['status']+' for the declared MACM6 substep only. '+p['acceptance']+' '+p.get('claim_scope','G0B-T03/T04 scientific completion flags remain unchanged; the source stationary sequence, CUDA comparison and physical eigenvalues are not evaluated here.'),
            'anomalies':f"- Dirty Git tree: {metadata['uncommitted_diff']}.\n- No CUDA execution; CLOUD paused; remote runner disabled.\n"+'\n'.join('- '+line for line in p.get('limitations',['Source initializer/archive absent; compact fixture independently derived.','Small-grid raw charge is not certified as unit topology.','CPU SciPy chart adapter has separate equivalence scope.','Vacuum smoke tests do not establish a nontrivial stationary soliton.']))+'\n'+(f"- {result['anomaly']}\n" if result.get('anomaly') else ''),
            'artifacts':'\n'.join(artifacts)+'\nSmall verification metrics/catalogs are sealed in result.json; no stationary checkpoint or dense lattice Hessian is produced.',
            'reproduction':f"```sh\n.venv/bin/python scripts/run.py --config {metadata['config_path']}\n.venv/bin/python scripts/report.py --run-id EXACT_NEW_RUN_ID\n```\nUse isolated checkout `{metadata['git_commit']}` with the exact source PDF and requirements/macm6.freeze.txt; task must be RUNNING/unfinished.",
            'changes':p.get('changes','First independent solver/HVP/CPU-DFT preparation report. No published numerical target, source acceptance tolerance, GPU completion flag or model coefficient changes.'),
            'next_action':p['next_action'],
            'handoff':'NEXT.md, MACHINE_HANDOFF.md, docs/MACM6_COMPLETION_PLAN.md and '+p['contract_doc'],
        })
    if metadata["machine"] == "RTX5070":
        python = ".venv/Scripts/python.exe" if metadata["os"].startswith("Windows") else ".venv/bin/python"
        values["reproduction"] = (
            f"```sh\n{python} -m pip install torch=={metadata['pytorch']} --index-url https://download.pytorch.org/whl/cu128\n"
            f"{python} -m pip install -r requirements/rtx5070.freeze.txt\n"
            f"{python} scripts/run.py --check --config {metadata['config_path']}\n"
            f"{python} scripts/run.py --config {metadata['config_path']}\n"
            f"{python} scripts/report.py --run-id EXACT_NEW_RUN_ID\n```\n"
            f"Use isolated checkout `{metadata['git_commit']}` with the matching PDF and frozen environment. "
            "The assigned responsibility must be RUNNING/unfinished and its preceding CUDA reports must pass."
        )
        values["inputs"] = values["inputs"].replace(
            "The user explicitly deferred RTX5070 while requesting MACM6 preparation. ",
            "The user resumed RTX5070 for the actual CUDA comparison. ")
        values["anomalies"] += (
            "\n- Actual RTX5070 environment/hardware (also sealed in metadata/environment JSON):\n```json\n"
            + json.dumps({"python": metadata["python"], "hardware": metadata["hardware"]}, indent=2)
            + "\n```\n- GitHub transfer has one upload commit; original MACM6 commit history is absent from this remote. "
            "Existing MACM6 report identities/evidence remain preserved.\n"
            "- Windows lacks symlink creation privilege; the security regression uses a directory junction to test the same path escape.\n"
        )
        values["changes"] = (
            "First actual RTX5070 float64 CUDA comparison against the preserved NumPy references. "
            "Records this Windows environment, driver, runtime, RAM/VRAM and exact input hashes. "
            "Restores missing transfer directories/ignore rules and uses machine-specific execution paths. "
            "Published tolerances and MACM6 completion records are unchanged."
        )
        if result["status"] == "PASS":
            values["next_action"] = {
                "G0A-T02": "Record only RTX5070 completion, then follow NEXT for G0B-T01 CUDA. MACM6 G0A-T03 already passed.",
                "G0B-T01": "Record only RTX5070 completion, then follow NEXT for the frozen G0B-T02 CUDA Hopf comparison.",
                "G0B-T02": "Record only RTX5070 completion, then develop G0B-T03 production driver and the matched stationary sequence. G0B-T04 spectrum remains pending; this initial field is nonstationary.",
            }[metadata["task"]]
        else:
            values["next_action"] = "Preserve this failed run/report, classify the anomaly and perform the smallest discriminating check before an explicit recovery. Do not loosen tolerances or advance the queue."
    report = ROOT / f"reports/{metadata['task'][:2]}" / f"{metadata['task']}__{args.run_id}__REPORT.md"
    output=(ROOT / "reports/SUBSTEP_REPORT_TEMPLATE.md").read_text(encoding="utf-8").format(**values)
    if seal_hash:
        output=output.replace(f"precision: {metadata['precision']}\n",f"precision: {metadata['precision']}\nevidence_sha256: {seal_hash}\n",1)
    output=output.replace('## Objective',f"report_generator_sha256: {sha256(ROOT/'scripts/report.py')}\n\n## Objective",1)
    with report.open("x", encoding="utf-8") as stream:
        stream.write(output)
    print(report.relative_to(ROOT).as_posix())
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, KeyError, OSError) as error:
        print(f"report: {error}", file=sys.stderr)
        raise SystemExit(1)
