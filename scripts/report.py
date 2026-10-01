"""Create one evidence-backed report for a predeclared setup/core substep."""
from __future__ import annotations

import argparse
import json
import sys

from common import ROOT, inside, read_data, sha256
from provenance import verify_run


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    run = inside(ROOT, f"runs/{args.run_id}", "runs")
    metadata, result = read_data(run / "metadata.json"), read_data(run / "result.json")
    if metadata["run_id"] != args.run_id or result["run_id"] != args.run_id:
        raise ValueError("Run ID does not match evidence")
    if metadata["task"] not in {"G0A-T01", "G0A-T02", "G0A-T03",'G0B-T01'}:
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
    report = ROOT / "reports/G0" / f"{metadata['task']}__{args.run_id}__REPORT.md"
    output=(ROOT / "reports/SUBSTEP_REPORT_TEMPLATE.md").read_text(encoding="utf-8").format(**values)
    if seal_hash:
        output=output.replace(f"precision: {metadata['precision']}\n",f"precision: {metadata['precision']}\nevidence_sha256: {seal_hash}\n",1)
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
