"""Source-only manufactured pilot contract checks; no FEM or manager import."""
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

from . import manufactured_driver as driver
from .manufactured_driver import assemble_diagnostics, validate_worker_payload
from .manufactured_manifest import contract_digest, expected, validate
from .manufactured_policy import compare
from .manufactured_report import build_report, validate_report
from .linear_evidence import LatestSystem
from .package_identity import FFCX_ARTIFACT, FFCX_RUNTIME, RECOVERY_EVIDENCE
from .prototype import Refusal
from .source_binding import expected_binding
from .sparse import CSR
from .sparse import condition_from_gram
from .supervision import supervise_manufactured_once
from .test_driver_supervision import Clock, FakeBackend
from . import manufactured_worker


PROPOSAL = expected()
REFERENCE = PROPOSAL['exact_reference']
MANIFEST = Path(__file__).with_name('future_manufactured.json')


def rational(value):
    return float(Fraction(value))


def exact_raw():
    final = REFERENCE['exact']
    raw = {key: 0. for key in PROPOSAL['diagnostic_policy']['raw_keys']}
    raw.update(volume=1., area_0=1., area_1=1.,
        boundary_absolute_flux=5., lateral_flux=rational(final['Q_lateral']),
        flux_0=rational(final['Q_minus']), flux_1=rational(final['Q_plus']),
        kinetic_energy=rational(final['kinetic_final']),
        angular_momentum=rational(final['angular_final']),
        **{'u_L2_squared': .001, 'u_H1_seminorm_squared': .002,
           'p_error_squared': .003, 'traction_L2_returns_squared': .004,
           'energy_identity_dissipation': rational(final['be_energy_dissipation'])})
    for kind in ('angular', 'energy'):
        for key, value in REFERENCE[kind+'_terms'].items():
            raw[kind+'.'+key] = rational(value)
    raw['energy_identity_storage'] = (raw['kinetic_energy']
        -rational(final['kinetic_initial']))/PROPOSAL['dt']
    raw['kinetic_discrete_derivative'] = raw['energy_identity_storage']
    return raw


def evidence(raw=None):
    raw = exact_raw() if raw is None else raw
    condition = condition_from_gram([[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])
    targets = [rational(REFERENCE['exact'][key]) for key in ('Q_minus', 'Q_plus')]
    lateral = rational(REFERENCE['exact']['Q_lateral'])
    lateral_absolute = 5.
    absolute = lateral_absolute+sum(map(abs, targets))
    compatibility = dict(defect=lateral+sum(targets),
        limit=128*2.220446049250313e-16*absolute,
        condition=1., absolute_term_sum=absolute, lateral_flux=lateral,
        targets=targets)
    correction = dict(true_residual=0., rhs_norm=1.,
        linear_system=dict(file='linear_system.json', correction=1,
                           sha256='a'*64, bytes=100))
    return dict(raw_by_degree={'24': deepcopy(raw), '26': deepcopy(raw)},
        multipliers=[rational(REFERENCE['exact'][key]) for key in ('P_minus', 'P_plus')],
        eta=0., history=[1., 0.], corrections=[correction], minimum_normal=.5,
        sample_counts=[10, 10], condition=condition, compatibility=compatibility,
        measured_targets=targets, lateral_absolute_flux=lateral_absolute,
        proposal=PROPOSAL)


class ManufacturedIntegrationChecks(unittest.TestCase):
    def test_be_roundoff_bound_keeps_three_signed_terms(self):
        from .manufactured_report import _be_identity
        from sys import float_info
        # Cancellation makes a two-value scale much smaller than the contract.
        raw = {'energy.storage': 1e-3, 'energy_identity_storage': -1e6,
               'energy_identity_dissipation': 1e6}
        check = _be_identity(raw, PROPOSAL['gates'])
        self.assertEqual(check['limit'], 128*float_info.epsilon*(2e6+1e-3))
        self.assertFalse(check['accepted'])
        raw['energy.storage'] = 1e-8
        self.assertTrue(_be_identity(raw, PROPOSAL['gates'])['accepted'])

    def test_frozen_proposal_and_exact_reference(self):
        self.assertEqual(validate(json.loads(MANIFEST.read_text())), PROPOSAL)
        for key in ('strain_l2_squared', 'be_energy_dissipation', 'Q_minus', 'Q_plus'):
            self.assertNotEqual(Fraction(REFERENCE['exact'][key]), 0)
        self.assertEqual(sum(Fraction(REFERENCE['angular_terms'][key])
            for key in ('storage', 'advective', 'traction', 'body')), 0)
        self.assertEqual(sum(Fraction(REFERENCE['energy_terms'][key])
            for key in ('storage', 'advective', 'traction', 'body', 'dissipation',
                        'conservative_divergence', 'pressure_divergence')), 0)
        self.assertTrue(all(Fraction(v) != 0 for v in REFERENCE['negative_controls'].values()))
        for key, bad in [('schema', True), ('execution_admitted', True),
                         ('attempts_granted', 1), ('diagnostic_policy', {}),
                         ('exact_reference', {}), ('extra', 1)]:
            with self.subTest(key=key), self.assertRaises(Refusal):
                validate(dict(PROPOSAL, **{key: bad}))

    def test_pair_floor_and_complete_numerical_replay(self):
        data = evidence()
        report = build_report(**data)
        self.assertTrue(report['numerical_accepted'])
        self.assertGreater(report['degree_validation']['24']['field_report']['u_L2'], 1e-9)
        self.assertIs(validate_report(report, PROPOSAL, **{k:v for k,v in data.items()
            if k not in ('raw_by_degree', 'proposal')}), report)
        base, check = data['raw_by_degree']['24'], data['raw_by_degree']['26']
        check['pressure_mean'] = 9e-15
        self.assertTrue(compare(base, check, PROPOSAL['diagnostic_policy'])['pressure_mean']['accepted'])
        check['pressure_mean'] = 1.1e-14
        self.assertFalse(compare(base, check, PROPOSAL['diagnostic_policy'])['pressure_mean']['accepted'])
        self.assertFalse(build_report(**data)['numerical_accepted'])

    def test_refuses_defects_in_each_degree_and_cached_flags(self):
        data = evidence()
        for degree in ('24', '26'):
            mutated = deepcopy(data)
            mutated['raw_by_degree'][degree]['energy.body'] += .1
            with self.subTest(degree=degree):
                self.assertFalse(build_report(**mutated)['numerical_accepted'])
        for mutate in (
            lambda item: item['raw_by_degree']['24'].update(u_L2_squared=True),
            lambda item: item['raw_by_degree']['26'].update(u_L2_squared=-1.),
            lambda item: item['raw_by_degree']['24'].pop('volume'),
            lambda item: item['raw_by_degree']['24'].update(extra=1.),
            lambda item: item['corrections'][0].update(true_residual=float('nan')),
            lambda item: item['condition'].update(condition_bound=True),
            lambda item: item['condition']['gram'][0].__setitem__(0, True),
        ):
            bad = deepcopy(data); mutate(bad)
            with self.assertRaises(Refusal): build_report(**bad)
        report = build_report(**data)
        report['checks']['degree24'] = False
        with self.assertRaises(Refusal):
            validate_report(report, PROPOSAL, **{k:v for k,v in data.items()
                if k not in ('raw_by_degree', 'proposal')})

    def test_independent_step_budget_and_identity_gates(self):
        changes = (
            lambda item: item['raw_by_degree']['24'].update(flux_0=.625+1e-5),
            lambda item: item['raw_by_degree']['24'].update(pressure_mean=1e-5),
            lambda item: item.update(eta=1e-5),
            lambda item: item.update(history=[1.,1e-3]),
            lambda item: item['corrections'][0].update(true_residual=1e-4),
            lambda item: item.update(minimum_normal=-1e-4),
            lambda item: item['raw_by_degree']['24'].update(**{
                'energy_identity_dissipation':
                    item['raw_by_degree']['24']['energy_identity_dissipation']+.01}),
            lambda item: item['raw_by_degree']['24'].update(angular_momentum=.1),
            lambda item: item['raw_by_degree']['26'].update(**{
                'energy.traction':item['raw_by_degree']['26']['energy.traction']+.1}),
        )
        for index,change in enumerate(changes):
            data=evidence();change(data)
            with self.subTest(index=index):
                self.assertFalse(build_report(**data)['numerical_accepted'])
        bad=evidence()
        bad['condition']['gram'][2][2]=1e-14
        with self.assertRaises(Refusal): build_report(**bad)
        bad=evidence()
        bad['raw_by_degree']['24']['p_error_squared']=0.
        bad['raw_by_degree']['24']['p_error_integral']=1.
        with self.assertRaises(Refusal): build_report(**bad)

    def test_admission_refuses_before_directory_or_backend(self):
        with TemporaryDirectory() as parent:
            path = Path(parent)/'run'
            with self.assertRaises(Refusal):
                supervise_manufactured_once(path, MANIFEST, None, object(),
                    source_commit='a'*40, interpreter='/usr/bin/python3', owner='daisy')
            self.assertFalse(path.exists())
        self.assertEqual(PROPOSAL['attempts_granted'], 0)

    def test_saved_envelope_recomputes_and_refuses_mutations(self):
        with TemporaryDirectory() as parent:
            directory=Path(parent)
            binary=Path(sys.executable).resolve(strict=True)
            admission=dict(approved=True, fixture='manufactured',
                kind='manufactured_spatial_pilot', mode='single_be_spatial_pilot',
                worker_schema=1, attempts_granted=1,
                run_directory=str(directory.resolve()), source_commit='a'*40,
                manifest_sha256=hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
                contract_sha256=contract_digest(PROPOSAL),
                interpreter=sys.executable, executable=str(binary),
                executable_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
                artifact_inventory_sha256='b'*64)
            reservation=dict(status='RESERVED',fixture='manufactured',attempt=1,
                source_commit='a'*40,interpreter=sys.executable,owner='daisy',
                release_nonce='c'*32,wall_start_utc='2026-09-26T00:00:00Z',
                monotonic_start=0.,caps=PROPOSAL['proposed_caps'])
            for key in ('fixture','kind','mode','worker_schema','source_commit',
                        'manifest_sha256','contract_sha256','interpreter','executable',
                        'executable_sha256','artifact_inventory_sha256'):
                reservation[key]=admission[key]
            binding=expected_binding(Path(__file__).resolve().parents[2],
                                     reservation,sys.executable)
            driver.validate_reservation(reservation, admission, MANIFEST.read_bytes(),
                PROPOSAL, directory, sys.executable, 'daisy')
            for schema in (True, 1.):
                bad = dict(reservation, worker_schema=schema)
                with self.assertRaises(Refusal):
                    driver.validate_reservation(bad, admission, MANIFEST.read_bytes(),
                        PROPOSAL, directory, sys.executable, 'daisy')
            LatestSystem(directory, binding, fixture='manufactured')(
                CSR.from_rows([{i: 1.} for i in range(405)]), [0., 1.]+[0.]*403,
                state=[2.]+[0.]*404, scales=[1.]*405, fixed={0: 2.}, step=1, correction=1)
            data=(directory/'linear_system.json').read_bytes()
            saved=json.loads(data)
            state=evidence()
            state['corrections'][0]['linear_system'].update(
                sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))
            report=build_report(**state)
            raw=state['raw_by_degree']
            receipts={degree:{key:dict(method='fem.form+assemble_scalar',
                ufl_integrals=4 if key=='lateral_flux' else
                    2 if key=='traction_L2_returns_squared' else 1,
                compiled_rank=0) for key in raw[degree]} for degree in ('24','26')}
            payload=dict(worker_schema=1,fixture='manufactured',
                kind='manufactured_spatial_pilot',mode='single_be_spatial_pilot',
                manifest_sha256=admission['manifest_sha256'],
                contract_sha256=admission['contract_sha256'],source_binding=binding,
                geometry=deepcopy(driver.GEOMETRY),subdivisions=2,step=1,time=.125,dt=.125,
                history_semantics=PROPOSAL['history'],load_semantics=PROPOSAL['load'],
                mixed_dofs=402,global_dofs=405,fixed_velocity_dofs=1,
                fixed_inventory={'0':2.},perturbed_velocity_dof=1,perturbation=.05,
                multipliers=state['multipliers'],eta=state['eta'],
                constraint_condition=state['condition'],compatibility=state['compatibility'],
                measured_targets=state['measured_targets'],
                lateral_absolute_flux=state['lateral_absolute_flux'],
                frozen_row_scales=dict(minimum=1.,maximum=1.),
                nonlinear_history=state['history'],linear_corrections=state['corrections'],
                raw_by_degree=raw,assembly_receipts=receipts,
                backflow_sampling_degree=24,
                return_quadrature_sample_counts=state['sample_counts'],
                minimum_return_normal_velocity=state['minimum_normal'],report=report,
                phase_seconds=dict(mesh_and_lift=.1,primary_form_setup_jit=.2,
                    compatibility_rank_newton=.3,diagnostic_form_jit_assembly_sampling=.4),
                worker_intervals=dict(import_seconds=.1,
                    fixture_setup_jit_and_solve_seconds=1.),
                actual_versions=dict(PROPOSAL['versions'],ffcx=FFCX_RUNTIME),
                ffcx_artifact=dict(package=dict(FFCX_ARTIFACT),
                    embedded_version=FFCX_RUNTIME,
                    recovery_evidence=dict(RECOVERY_EVIDENCE)))
            self.assertIs(validate_worker_payload(payload,PROPOSAL,reservation,
                admission,directory),payload)
            mutations=(
                lambda p:p.update(time=.25),
                lambda p:p.update(load_semantics='continuous'),
                lambda p:p['geometry'].update(mixed_space_ghosts=False),
                lambda p:p['source_binding'].update(clean=1),
                lambda p:p['assembly_receipts']['26'].pop('volume'),
                lambda p:p['report']['checks'].update(quadrature=False),
                lambda p:p['linear_corrections'][0]['linear_system'].update(sha256='0'*64),
                lambda p:p['actual_versions'].update(dolfinx='0.0.0'),
            )
            for index,change in enumerate(mutations):
                bad=deepcopy(payload);change(bad)
                with self.subTest(index=index),self.assertRaises(Refusal):
                    validate_worker_payload(bad,PROPOSAL,reservation,admission,directory)
            # Rehash each malformed record, so these test content validation.
            for change in (
                lambda s:s.pop('csr'),
                lambda s:s['csr']['indptr'].__setitem__(0, 1),
                lambda s:s['csr']['values'].__setitem__(0, True),
                lambda s:s['rhs'].__setitem__(1, 2.),
                lambda s:s['state'].__setitem__(0, 3.),
                lambda s:s['row_scales'].__setitem__(1, .5),
                lambda s:s['solver'].update(shift='nonzero'),
            ):
                altered=deepcopy(saved); change(altered)
                blob=(json.dumps(altered,sort_keys=True)+'\n').encode()
                (directory/'linear_system.json').write_bytes(blob)
                bad=deepcopy(payload)
                bad['linear_corrections'][-1]['linear_system'].update(
                    sha256=hashlib.sha256(blob).hexdigest(),bytes=len(blob))
                with self.assertRaises(Refusal):
                    validate_worker_payload(bad,PROPOSAL,reservation,admission,directory)

    def test_fixture_dispatch_preserves_incomplete_attempts(self):
        for settings in (dict(write_result=False),
                         dict(write_result=False, exit_code=1),
                         dict(write_result=False, work_seconds=151),
                         dict(write_result=False, cleanup_ok=False)):
            with self.subTest(settings=settings), TemporaryDirectory() as parent:
                directory = Path(parent)/'run'
                binary = Path(sys.executable).resolve(strict=True)
                admission = dict(approved=True, fixture='manufactured',
                    kind='manufactured_spatial_pilot', mode='single_be_spatial_pilot',
                    worker_schema=1, attempts_granted=1,
                    run_directory=str(directory.resolve()), source_commit='a'*40,
                    manifest_sha256=hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
                    contract_sha256=contract_digest(PROPOSAL),
                    interpreter=sys.executable, executable=str(binary),
                    executable_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
                    artifact_inventory_sha256='b'*64)
                clock = Clock()
                backend = FakeBackend(clock, **settings)
                result = supervise_manufactured_once(directory, MANIFEST, admission,
                    backend, source_commit='a'*40, interpreter=sys.executable,
                    owner='daisy', monotonic=clock)
                self.assertEqual(result['status'], 'INCOMPLETE')
                self.assertTrue((directory/'reservation.json').exists())
                self.assertTrue(backend.handle.stopped)
                self.assertTrue((directory/'completion.json').exists())

    def test_both_degrees_route_all_form_assemblies_and_exact_context(self):
        keys = PROPOSAL['diagnostic_policy']['raw_keys']
        calls = []
        domain = NS(ufl_domain=lambda: domain)
        tags = object()
        class Integral:
            def __init__(self, kind, tag=None): self.kind, self.tag=kind,tag
            def integral_type(self): return self.kind
            def subdomain_id(self): return self.tag
            def subdomain_data(self): return tags
        class Form:
            def __init__(self, key):
                self.key=key
                if key == 'lateral_flux': ids=(1,2,3,4)
                elif key == 'traction_L2_returns_squared': ids=(5,6)
                elif key.startswith(('area_', 'flux_')): ids=(5+int(key[-1]),)
                else: ids=(None,)
                boundary=(key.startswith(('area_', 'flux_')) or key in {
                    'lateral_flux','boundary_absolute_flux','traction_L2_returns_squared',
                    'angular.advective','angular.traction','energy.advective','energy.traction'})
                self.parts=[Integral('exterior_facet' if boundary else 'cell', i) for i in ids]
            def arguments(self): return ()
            def integrals(self): return self.parts
            def ufl_domains(self): return (domain,)
        class FEM:
            def form(self, form): calls.append(('form',form.key)); return NS(rank=0, key=form.key)
            def assemble_scalar(self, form): calls.append(('assemble',form.key)); return 0.
        U=NS(Form=Form, Measure=lambda *args,**kw: None)
        modules=dict(ufl=U, fem=FEM())
        context=dict(history=('exact-old','exact-old'), force='corrected-BE',
                     exact='exact-new', raw_keys=keys)
        def forms(_U,_domain,_w,prev,older,exact,force,*rest):
            self.assertEqual((prev,older,exact,force),
                ('exact-old','exact-old','exact-new','corrected-BE'))
            return {key:Form(key) for key in keys}
        with patch('verification.nonlinear_port.manufactured_driver.field_forms', forms), patch('builtins.print'):
            for degree in (24,26):
                raw, receipts=assemble_diagnostics(modules,domain,tags,object(),context,degree)
                self.assertEqual(set(raw),set(keys)); self.assertEqual(len(receipts),30)
        self.assertEqual(len(calls),120)

    def test_driver_uses_corrected_load_exact_history_and_checked_correction(self):
        class Array(list):
            def tolist(self): return list(self)
        target = [2.]+[0.]*401+[rational(REFERENCE['exact']['P_minus']),
                                 rational(REFERENCE['exact']['P_plus']),0.]
        space = NS(sub=lambda _: NS(collapse=lambda: (None,list(range(402)))))
        def function(_space):
            return NS(x=NS(array=Array(target[:402]),scatter_forward=lambda:None),
                      sub=lambda _:NS(collapse=lambda:None))
        fem = NS(Function=function, form=lambda value:value,
                 assemble_scalar=unittest.mock.Mock(side_effect=[
                     rational(REFERENCE['exact']['Q_lateral']),5.,
                     rational(REFERENCE['exact']['Q_minus']),
                     rational(REFERENCE['exact']['Q_plus'])]))
        U=unittest.mock.MagicMock()
        U.split.return_value=(unittest.mock.MagicMock(),unittest.mock.MagicMock())
        modules=dict.fromkeys(['np','mesh','fem_petsc','basix_ufl','basix','PETSc'])
        modules.update(fem=fem,ufl=U,comm=NS(size=1))
        class Assembler:
            rows=(0,1,2)
            def __init__(self,*args): pass
            def vector(self,index):
                return [[float(i==j) for i in range(402)] for j in (1,2,3)][index]
            def __call__(self,state):
                self_outer.assertEqual(len(state),405)
                return [value-want for value,want in zip(state,target)], CSR.from_rows(
                    [{i:1.} for i in range(405)])
        self_outer=self
        degrees=[]
        def step(*args, **kwargs):
            degree=kwargs['degree']; degrees.append(degree)
            return {}, [], dict(exact={'targets':[U,U]}, ds=unittest.mock.MagicMock(),
                force='corrected-BE', history=('exact-old','exact-old'))
        routed=[]
        def diagnostics(_modules,_domain,_tags,_w,context,degree):
            routed.append((degree,context['history'],context['force']))
            raw=exact_raw()
            receipts={key:dict(method='fem.form+assemble_scalar',
                ufl_integrals=4 if key=='lateral_flux' else
                              2 if key=='traction_L2_returns_squared' else 1,
                compiled_rank=0) for key in raw}
            return raw,receipts
        saved=[]
        def latest(matrix,rhs,**kw):
            saved.append(kw)
            return dict(file='linear_system.json',correction=kw['correction'],
                        sha256='a'*64,bytes=100)
        with (patch.object(driver,'create_cube',return_value=(None,space,None,None)),
              patch.object(driver,'measured_geometry',return_value=driver.GEOMETRY),
              patch.object(driver,'interpolate_state',side_effect=lambda *a:function(space)),
              patch.object(driver,'boundary_values',return_value={0:2.}),
              patch.object(driver,'step_forms',side_effect=step),
              patch.object(driver,'Assembler',Assembler),
              patch.object(driver,'sparse_solve',side_effect=lambda np,p,c,m,r:r) as solver,
              patch.object(driver,'assemble_diagnostics',side_effect=diagnostics),
              patch.object(driver,'return_quadrature_samples',return_value=([.5,.5],[1,1]))):
            result=driver.run_manufactured(modules,PROPOSAL,linear_evidence=latest)
            solver.reset_mock()
            fem.assemble_scalar.side_effect=[
                rational(REFERENCE['exact']['Q_lateral']),5.,
                rational(REFERENCE['exact']['Q_minus']),
                rational(REFERENCE['exact']['Q_plus'])]
            def refuse_latest(*args,**kwargs):
                raise OSError('linear evidence save refused')
            with self.assertRaisesRegex(OSError,'linear evidence save refused'):
                driver.run_manufactured(modules,PROPOSAL,
                                        linear_evidence=refuse_latest)
            solver.assert_not_called()
        self.assertEqual(degrees,[24,26,24])
        self.assertEqual(routed,[(24,('exact-old','exact-old'),'corrected-BE'),
                                 (26,('exact-old','exact-old'),'corrected-BE')])
        self.assertEqual(len(saved),1)
        self.assertEqual(saved[0]['correction'],1)
        self.assertEqual((result['mixed_dofs'],result['global_dofs']),(402,405))
        self.assertEqual(result['perturbed_velocity_dof'],1)
        self.assertTrue(result['report']['numerical_accepted'])

    def test_held_refusal_precedes_numerical_import(self):
        with TemporaryDirectory() as parent:
            directory=Path(parent)
            with (patch.object(manufactured_worker, 'read_limited', side_effect=[{},{}]),
                  patch.object(manufactured_worker, 'strict_json_bytes', return_value=PROPOSAL),
                  patch.object(manufactured_worker, 'validate_reservation'),
                  patch.object(manufactured_worker, 'verify_source', return_value={}),
                  patch.object(manufactured_worker, '_cgroup_path', return_value='/test'),
                  patch.object(manufactured_worker, 'held', side_effect=Refusal('held refused')),
                  patch.object(manufactured_worker, 'load_pinned_modules') as load):
                manifest=directory/'manifest.json'; manifest.write_text('{}')
                with self.assertRaises(Refusal):
                    manufactured_worker.main([str(directory),str(manifest)])
                load.assert_not_called()
