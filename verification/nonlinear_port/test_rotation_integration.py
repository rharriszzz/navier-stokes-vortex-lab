"""Source-only rotation integration controls; all FEM and manager calls are fakes."""
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

from .package_identity import FFCX_ARTIFACT, FFCX_RUNTIME, RECOVERY_EVIDENCE
from .prototype import Refusal
from .rotation_driver import (GEOMETRY, assemble_rotation, expected_admission,
    read_limited, strict_json_bytes, validate_worker_payload, write_limited_new)
from .rotation_manifest import contract_digest, expected, validate
from .rotation_oracle import build_report
from .source_binding import expected_binding
from .supervision import supervise_once, supervise_rotation_once
from .systemd_backend import Handle
from .test_driver_supervision import Clock, FakeBackend, FakeHandle, SOURCE
from . import rotation_worker, supervision

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = Path(__file__).with_name('future_rotation.json')
PROPOSAL = json.loads(MANIFEST.read_text())
ARTIFACT = dict(package=dict(FFCX_ARTIFACT), embedded_version=FFCX_RUNTIME,
                recovery_evidence=dict(RECOVERY_EVIDENCE))


def proposal_admission(path, **changes):
    binary = Path(sys.executable).resolve(strict=True)
    result = dict(approved=True, kind='rotation_assembly', fixture='rotation',
                  mode='exact_field_assembly', worker_schema=1, attempts_granted=1,
                  run_directory=str(path.resolve()), source_commit=SOURCE,
                  manifest_sha256=hashlib.sha256(MANIFEST.read_bytes()).hexdigest(),
                  contract_sha256=contract_digest(PROPOSAL['contract']),
                  interpreter=sys.executable, executable=str(binary),
                  executable_sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
                  artifact_inventory_sha256='a'*64)
    result.update(changes)
    return result


def reservation(admission):
    result = dict(status='RESERVED', fixture='rotation', attempt=1,
                  source_commit=SOURCE, interpreter=sys.executable, owner='daisy',
                  release_nonce='b'*32, wall_start_utc='2026-09-26T22:00:00Z',
                  monotonic_start=0.0, caps=PROPOSAL['proposed_caps'])
    for key in ('kind', 'mode', 'worker_schema', 'manifest_sha256', 'contract_sha256',
                'executable', 'executable_sha256', 'artifact_inventory_sha256'):
        result[key] = admission[key]
    return result


def envelope(saved_reservation, **changes):
    raw = {key: float(Fraction(value)) for key, value in
           PROPOSAL['contract']['raw_targets_rational'].items()}
    keys = raw.keys()
    result = dict(worker_schema=1, kind='rotation_assembly', fixture='rotation',
                  mode='exact_field_assembly',
                  manifest_sha256=saved_reservation['manifest_sha256'],
                  contract_sha256=saved_reservation['contract_sha256'],
                  source_binding=expected_binding(ROOT, saved_reservation, sys.executable),
                  geometry=dict(GEOMETRY),
                  oracle=build_report({'24': dict(raw), '26': dict(raw)},
                                      PROPOSAL['contract']),
                  assembly_receipts={degree: {key: dict(method='fem.form+assemble_scalar',
                      ufl_integrals=6 if key.endswith('_traction_boundary_l2_squared') else 1,
                      compiled_rank=0) for key in keys} for degree in ('24','26')},
                  phase_seconds=dict(mesh_and_tags=0.1, degree24_form_jit_assembly=0.2,
                                     degree26_form_jit_assembly=0.2, report_reduction=0.01),
                  worker_intervals=dict(import_seconds=0.1,
                      fixture_setup_jit_and_assembly_seconds=0.51),
                  actual_versions=dict(PROPOSAL['versions'], ffcx=FFCX_RUNTIME),
                  ffcx_artifact=deepcopy(ARTIFACT))
    result.update(changes)
    return result


class FakeIntegral:
    def __init__(self, kind, tag, tags): self.kind, self.tag, self.tags = kind, tag, tags
    def integral_type(self): return self.kind
    def subdomain_id(self): return self.tag
    def subdomain_data(self): return self.tags


class FakeForm:
    def __init__(self, key, domain, tags):
        self.key, self.domain, self.tags = key, domain, tags
        boundary = (key.startswith(('area_', 'normal_')) or
                    key.endswith('_traction_boundary_l2_squared'))
        if boundary:
            ids = range(1,7) if key.endswith('_traction_boundary_l2_squared') else [int(key.split('_')[1])]
            self.parts = [FakeIntegral('exterior_facet', tag, tags) for tag in ids]
        else:
            self.parts = [FakeIntegral('cell', 'everywhere', None)]
    def arguments(self): return ()
    def integrals(self): return self.parts
    def ufl_domains(self): return (self.domain.ufl_domain(),)


class FakeDomain:
    def __init__(self):
        self.topology = NS(dim=3, cell_name=lambda: 'tetrahedron',
                           index_map=lambda dim: NS(size_global=27 if dim==0 else 48))
        self.geometry = NS(dim=3)
    def ufl_domain(self): return self


class FakeFEM:
    def __init__(self, values): self.values, self.calls = values, []
    def form(self, form):
        self.calls.append(('form', form.key)); return NS(rank=0, original=form)
    def assemble_scalar(self, compiled):
        self.calls.append(('assemble', compiled.original.key))
        return self.values[compiled.original.key]
    def interpolate_state(self, *args): raise AssertionError('solver/interpolation used')
    def step_forms(self, *args): raise AssertionError('PDE forms used')


class RotationHandle(FakeHandle):
    def __init__(self, directory, clock, *, mutate=None, **kwargs):
        super().__init__(directory, clock, **kwargs); self.mutate=mutate
    def wait(self, timeout):
        assert timeout==150 and self.released
        self.clock.value += self.work_seconds
        if self.write_result:
            saved=json.loads((self.directory/'reservation.json').read_text())
            value=envelope(saved)
            if self.mutate: self.mutate(value)
            (self.directory/'numerical.json').write_text(json.dumps(value))
        return {'exit_code': self.exit_code}


class RotationBackend(FakeBackend):
    def start_held(self, command, directory, caps):
        self.command = command
        self.handle=RotationHandle(directory, self.clock, **self.kwargs)
        return self.handle


class RotationIntegrationChecks(unittest.TestCase):
    def test_exact_proposal_and_preflight_refusal(self):
        self.assertEqual(validate(PROPOSAL), expected())
        with TemporaryDirectory() as base:
            path=Path(base)/'run'; clock=Clock(); backend=RotationBackend(clock)
            admission=proposal_admission(path)
            expected_admission(admission, MANIFEST.read_bytes(), PROPOSAL,
                               path, SOURCE, sys.executable, 'daisy')
            for key, bad in [('fixture','poiseuille'), ('worker_schema',True),
                             ('contract_sha256','0'*64), ('executable_sha256','0'*64),
                             ('artifact_inventory_sha256','0')]:
                with self.subTest(key=key), self.assertRaises(Refusal):
                    supervise_rotation_once(path, MANIFEST, dict(admission, **{key:bad}),
                        backend, source_commit=SOURCE, interpreter=sys.executable,
                        owner='daisy', monotonic=clock)
            self.assertFalse(path.exists()); self.assertIsNone(backend.handle)
            with self.assertRaises(Refusal):
                supervise_rotation_once(path, MANIFEST, admission, None,
                    source_commit=SOURCE, interpreter=sys.executable, owner='daisy')
            self.assertFalse(path.exists())
            with self.assertRaises(Refusal):
                supervise_once(path, MANIFEST, admission, backend,
                    source_commit=SOURCE, interpreter=sys.executable, owner='daisy')
            self.assertFalse(path.exists())
        for key, bad in [('execution_admitted',True), ('attempts_granted',1),
                         ('schema',True), ('contract',{}), ('versions',{}),
                         ('proposed_caps',{}), ('extra',1)]:
            with self.subTest(key=key), self.assertRaises(Refusal):
                validate(dict(PROPOSAL, **{key:bad}))
        self.assertEqual(strict_json_bytes(b'{"a":1}'), {'a':1})
        for data in (b'{"a":1,"a":2}', b'{"a":NaN}', b'{} trailing', b'\xff'):
            with self.assertRaises(Refusal): strict_json_bytes(data)

    def test_assembly_all_76_keys_with_zero_values_and_geometry(self):
        values={k:float(Fraction(v)) for k,v in PROPOSAL['contract']['raw_targets_rational'].items()}
        domain=FakeDomain(); tags=NS(indices=list(range(48)),values=[tag for tag in range(1,7) for _ in range(8)])
        space=NS(dofmap=NS(index_map=NS(size_global=402,num_ghosts=0),index_map_bs=1))
        fem=FakeFEM(values)
        modules=dict(np=object(), mesh=NS(exterior_facet_indices=lambda topology:list(range(48))),
                     fem=fem,basix_ufl=object(),comm=NS(size=1),ufl=NS(Form=FakeForm))
        forms=[]
        def make_forms(U, d, t, degree):
            forms.append(degree)
            return {key:FakeForm(key,d,t) for key in values}
        with (patch('verification.nonlinear_port.rotation_driver.create_cube',
                    return_value=(domain,space,tags,[])) as cube,
              patch('verification.nonlinear_port.rotation_driver.rotation_forms',make_forms),
              patch('builtins.print')):
            geometry,oracle,receipts,phases=assemble_rotation(modules,PROPOSAL)
        cube.assert_called_once(); self.assertEqual(cube.call_args.args[-2:],(2,'rotation'))
        self.assertEqual(geometry,GEOMETRY); self.assertEqual(forms,[24,26])
        self.assertEqual(len(fem.calls),152); self.assertEqual(sum(c[0]=='assemble' for c in fem.calls),76)
        self.assertEqual(oracle['numerical_accepted'],True)
        self.assertEqual(oracle['raw_by_degree']['24']['strain_l2_squared'],0.0)
        self.assertEqual(len(receipts['24']),38); self.assertEqual(set(phases),
            {'mesh_and_tags','degree24_form_jit_assembly','degree26_form_jit_assembly','report_reduction'})
        self.driver_setup=(domain,space,tags,fem,modules,values)

    def test_bad_form_scalar_and_geometry_refuse(self):
        values={k:float(Fraction(v)) for k,v in PROPOSAL['contract']['raw_targets_rational'].items()}
        domain=FakeDomain(); tags=NS(indices=list(range(48)),values=[tag for tag in range(1,7) for _ in range(8)])
        space=NS(dofmap=NS(index_map=NS(size_global=402,num_ghosts=0),index_map_bs=1))
        fem=FakeFEM(values)
        modules=dict(np=object(),mesh=NS(exterior_facet_indices=lambda topology:list(range(48))),
                     fem=fem,basix_ufl=object(),comm=NS(size=1),ufl=NS(Form=FakeForm))
        def attempt(change):
            def make(U,d,t,degree):
                forms={key:FakeForm(key,d,t) for key in values}; change(forms); return forms
            with (patch('verification.nonlinear_port.rotation_driver.create_cube',return_value=(domain,space,tags,[])),
                  patch('verification.nonlinear_port.rotation_driver.rotation_forms',make),
                  patch('builtins.print')):
                assemble_rotation(modules,PROPOSAL)
        for bad in (lambda f:f.__setitem__('strain_l2_squared',object()),
                    lambda f:setattr(f['volume'],'parts',[]),
                    lambda f:setattr(f['volume'],'ufl_domains',lambda:()),
                    lambda f:setattr(f['area_1'],'parts',[FakeIntegral('exterior_facet',2,tags)]),
                    lambda f:setattr(f['total_traction_boundary_l2_squared'],'parts',
                        [FakeIntegral('exterior_facet',5,tags),FakeIntegral('exterior_facet',6,tags)])):
            with self.subTest(bad=bad),self.assertRaises(Refusal): attempt(bad)
        for value in (float('nan'),complex(0),[0],True):
            with self.subTest(value=value),self.assertRaises(Refusal):
                previous=fem.values['volume']; fem.values['volume']=value
                try: attempt(lambda f:None)
                finally: fem.values['volume']=previous
        original=fem.form
        fem.form=lambda form: NS(rank=1,original=form)
        with self.assertRaises(Refusal): attempt(lambda f:None)
        fem.form=lambda form: (_ for _ in ()).throw(RuntimeError('JIT failed'))
        with self.assertRaisesRegex(Refusal,'degree=24 key=area_1'): attempt(lambda f:None)
        fem.form=original
        tags.values[0]=2
        with self.assertRaises(Refusal): attempt(lambda f:None)

    def test_envelope_recomputation_and_size_limits(self):
        with TemporaryDirectory() as base:
            path=Path(base)/'run'; admission=proposal_admission(path); saved=reservation(admission)
            value=envelope(saved)
            self.assertIs(validate_worker_payload(value,PROPOSAL,saved,admission),value)
            changes=[lambda p:p.__setitem__('fixture','poiseuille'),
                     lambda p:p.__setitem__('worker_schema',True),
                     lambda p:p['oracle']['raw_by_degree']['24'].__setitem__('pressure_l2_squared',0.),
                     lambda p:p['oracle']['raw_by_degree']['26'].__setitem__('momentum_residual_l2_squared',1/6),
                     lambda p:p['oracle']['raw_by_degree']['24'].__setitem__('strain_l2_squared',-1e-30),
                     lambda p:p['oracle']['degree_checks']['24'].__setitem__('accepted',False),
                     lambda p:p['geometry'].__setitem__('facet_counts',dict(p['geometry']['facet_counts'],**{'1':7})),
                     lambda p:p['assembly_receipts']['24'].__delitem__('area_1'),
                     lambda p:p['assembly_receipts']['26']['volume'].__setitem__('compiled_rank',True),
                     lambda p:p['assembly_receipts']['26']['total_traction_boundary_l2_squared'].__setitem__('ufl_integrals',2),
                     lambda p:p['source_binding'].__setitem__('clean',False),
                     lambda p:p['actual_versions'].__setitem__('ufl','0'),
                     lambda p:p['worker_intervals'].__setitem__('import_seconds',float('inf'))]
            for change in changes:
                bad=deepcopy(value); change(bad)
                with self.subTest(change=change),self.assertRaises(Refusal):
                    validate_worker_payload(bad,PROPOSAL,saved,admission)
            out=Path(base)/'report.json'; write_limited_new(out,value)
            self.assertEqual(read_limited(out),value)
            with self.assertRaises(FileExistsError): write_limited_new(out,value)
            oversized=dict(value, padding='x'*2_000_000)
            with self.assertRaises(Refusal): write_limited_new(Path(base)/'too_large',oversized)
            self.assertFalse((Path(base)/'too_large').exists())
            (Path(base)/'corrupt').write_bytes(b'{"a":1,"a":2}')
            with self.assertRaises(Refusal): read_limited(Path(base)/'corrupt')
            (Path(base)/'large').write_bytes(b'x'*2_000_001)
            with self.assertRaises(Refusal): read_limited(Path(base)/'large')

    def test_rotation_shared_lifecycle_and_cross_fixture(self):
        with TemporaryDirectory() as base:
            path=Path(base)/'run'; clock=Clock(); backend=RotationBackend(clock)
            admission=proposal_admission(path)
            result=supervise_rotation_once(path,MANIFEST,admission,backend,
                source_commit=SOURCE,interpreter=sys.executable,owner='daisy',monotonic=clock)
            self.assertEqual(result['status'],'PASS')
            self.assertEqual(backend.command[2],'verification.nonlinear_port.rotation_worker')
            self.assertTrue(backend.handle.stopped)
            self.assertEqual(json.loads((path/'completion.json').read_text())['status'],'PASS')
            with self.assertRaises(FileExistsError):
                supervise_rotation_once(path,MANIFEST,admission,backend,
                    source_commit=SOURCE,interpreter=sys.executable,owner='daisy',monotonic=clock)
        for kwargs in ({'write_result':False},{'exit_code':1},{'cleanup_ok':False},
                       {'work_seconds':151.}, {'mutate':lambda p:p['oracle'].__setitem__('numerical_accepted',False)},
                       {'mutate':lambda p:p.__setitem__('oracle',build_report(
                           {d:dict(p['oracle']['raw_by_degree'][d],pressure_l2_squared=0.)
                            for d in ('24','26')},PROPOSAL['contract']))}):
            with self.subTest(kwargs=kwargs),TemporaryDirectory() as base:
                path=Path(base)/'run'; clock=Clock(); backend=RotationBackend(clock,**kwargs)
                result=supervise_rotation_once(path,MANIFEST,proposal_admission(path),backend,
                    source_commit=SOURCE,interpreter=sys.executable,owner='daisy',monotonic=clock)
                self.assertEqual(result['status'],'INCOMPLETE')
                self.assertTrue((path/'reservation.json').exists())
                self.assertTrue(backend.handle.stopped)
                if kwargs.get('mutate'):
                    self.assertTrue((path/'numerical.json').exists())
        class Partial(RotationBackend):
            def start_held(self,command,directory,caps):
                self.active_handle=RotationHandle(directory,self.clock)
                raise Refusal('partial rotation start')
        with TemporaryDirectory() as base:
            path=Path(base)/'run';clock=Clock();backend=Partial(clock)
            result=supervise_rotation_once(path,MANIFEST,proposal_admission(path),backend,
                source_commit=SOURCE,interpreter=sys.executable,owner='daisy',monotonic=clock)
            self.assertEqual(result['status'],'INCOMPLETE');self.assertTrue(backend.active_handle.stopped)

    def test_backend_unit_name_is_fixture_locked_without_start(self):
        with TemporaryDirectory() as base:
            path=Path(base)
            (path/'reservation.json').write_text(json.dumps({'fixture':'rotation','release_nonce':'n'}))
            handle=Handle(ROOT,path,149)
            self.assertTrue(handle.unit.startswith('navier-rotation-'))
            (path/'reservation.json').write_text(json.dumps({'fixture':'unknown','release_nonce':'n'}))
            with self.assertRaises(Refusal): Handle(ROOT,path,149)

    def test_worker_held_order_and_refusals(self):
        with TemporaryDirectory() as base:
            path=Path(base)/'run';path.mkdir();admission=proposal_admission(path);saved=reservation(admission)
            (path/'reservation.json').write_text(json.dumps(saved));(path/'admission.json').write_text(json.dumps(admission))
            events=[]; value=envelope(saved)
            def hold(*args): events.append('held')
            def load(versions):
                self.assertIn('held',events);events.append('import')
                return {},value['actual_versions'],value['ffcx_artifact']
            def assemble(modules,manifest,*,monotonic):
                self.assertEqual(events,['held','import']);events.append('assemble')
                return (value['geometry'],value['oracle'],value['assembly_receipts'],value['phase_seconds'])
            def finish(*args): self.assertTrue((path/'numerical.json').exists());events.append('completed')
            env={name:'1' for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS')}
            with (patch.object(rotation_worker,'_cgroup_path',return_value='/test'),
                  patch.object(rotation_worker,'verify_source',return_value=value['source_binding']),
                  patch.object(rotation_worker,'held',side_effect=hold),
                  patch.object(rotation_worker,'load_pinned_modules',side_effect=load),
                  patch.object(rotation_worker,'assemble_rotation',side_effect=assemble),
                  patch.object(rotation_worker,'completed',side_effect=finish),
                  patch.dict(os.environ,env)):
                self.assertEqual(rotation_worker.main([str(path),str(MANIFEST)]),0)
            self.assertEqual(events,['held','import','assemble','completed'])
            (path/'reservation.json').write_text(json.dumps(dict(saved,release_nonce='bad')))
            with (patch.object(rotation_worker,'held') as held,
                  patch.object(rotation_worker,'load_pinned_modules') as loader):
                with self.assertRaises(Refusal): rotation_worker.main([str(path),str(MANIFEST)])
                held.assert_not_called();loader.assert_not_called()
            (path/'reservation.json').write_text(json.dumps(saved))
            with (patch.object(rotation_worker,'_cgroup_path',return_value='/test'),
                  patch.object(rotation_worker,'verify_source',return_value=value['source_binding']),
                  patch.object(rotation_worker,'held',side_effect=Refusal('wrong cgroup')),
                  patch.object(rotation_worker,'load_pinned_modules') as loader):
                with self.assertRaises(Refusal): rotation_worker.main([str(path),str(MANIFEST)])
                loader.assert_not_called()
            with (patch.object(rotation_worker,'_cgroup_path',return_value='/test'),
                  patch.object(rotation_worker,'verify_source',return_value=value['source_binding']),
                  patch.object(rotation_worker,'held',side_effect=hold),
                  patch.object(rotation_worker,'load_pinned_modules') as loader,
                  patch.dict(os.environ,{'OMP_NUM_THREADS':'2'})):
                with self.assertRaises(Refusal): rotation_worker.main([str(path),str(MANIFEST)])
                loader.assert_not_called()
            other=Path(base)/'failed_numerical'; other.mkdir()
            admission2=proposal_admission(other); saved2=reservation(admission2)
            (other/'reservation.json').write_text(json.dumps(saved2))
            (other/'admission.json').write_text(json.dumps(admission2))
            value2=envelope(saved2)
            wrong={degree:dict(value2['oracle']['raw_by_degree'][degree],pressure_l2_squared=0.)
                   for degree in ('24','26')}
            value2['oracle']=build_report(wrong,PROPOSAL['contract'])
            def failed_assembly(modules,manifest,*,monotonic):
                return (value2['geometry'],value2['oracle'],
                        value2['assembly_receipts'],value2['phase_seconds'])
            with (patch.object(rotation_worker,'_cgroup_path',return_value='/test'),
                  patch.object(rotation_worker,'verify_source',return_value=value2['source_binding']),
                  patch.object(rotation_worker,'held'),
                  patch.object(rotation_worker,'load_pinned_modules',
                               return_value=({},value2['actual_versions'],value2['ffcx_artifact'])),
                  patch.object(rotation_worker,'assemble_rotation',side_effect=failed_assembly),
                  patch.object(rotation_worker,'completed'),patch.dict(os.environ,env)):
                self.assertEqual(rotation_worker.main([str(other),str(MANIFEST)]),0)
            self.assertFalse(read_limited(other/'numerical.json')['oracle']['numerical_accepted'])

    def test_rotation_containment_persistence_and_late_refusals(self):
        for change in (
            lambda handle: setattr(handle, 'facts', lambda: dict(FakeHandle.facts(handle),
                                                                 swap_max_bytes=1)),
            lambda handle: setattr(handle, 'facts', lambda: dict(FakeHandle.facts(handle),
                                                                 worker_held=False)),
            lambda handle: setattr(handle, 'facts', lambda: dict(FakeHandle.facts(handle),
                                                                 independent_expiry_seconds=151)),
            lambda handle: setattr(handle, 'cleanup', lambda: dict(FakeHandle.cleanup(handle),
                                                                   memory_events={'max':1,'oom':0,'oom_kill':0})),
            lambda handle: setattr(handle, 'cleanup', lambda: dict(FakeHandle.cleanup(handle),
                                                                   pids_events={'max':1})),
            lambda handle: setattr(handle, 'cleanup', lambda: dict(FakeHandle.cleanup(handle),
                                                                   memory_peak_bytes=None)),
        ):
            class Altered(RotationBackend):
                def start_held(self, command, directory, caps):
                    handle=super().start_held(command,directory,caps)
                    change(handle)
                    return handle
            with self.subTest(change=change), TemporaryDirectory() as base:
                path=Path(base)/'run';clock=Clock();backend=Altered(clock)
                result=supervise_rotation_once(path,MANIFEST,proposal_admission(path),backend,
                    source_commit=SOURCE,interpreter=sys.executable,owner='daisy',monotonic=clock)
                self.assertEqual(result['status'],'INCOMPLETE')
                self.assertTrue(backend.handle.stopped)
                self.assertTrue((path/'reservation.json').exists())
                if 'held_scope' not in result:
                    self.assertFalse(backend.handle.released)
        with TemporaryDirectory() as base:
            path=Path(base)/'run';clock=Clock();backend=RotationBackend(clock)
            original=supervision._save_new
            def delayed(file,value):
                original(file,value)
                if file.name=='completion.json':clock.value+=16
            with patch.object(supervision,'_save_new',delayed):
                result=supervise_rotation_once(path,MANIFEST,proposal_admission(path),backend,
                    source_commit=SOURCE,interpreter=sys.executable,owner='daisy',monotonic=clock)
            self.assertEqual(result['status'],'INCOMPLETE')
            self.assertTrue((path/'late.json').exists())
        with TemporaryDirectory() as base:
            path=Path(base)/'run';clock=Clock();backend=RotationBackend(clock)
            original=supervision._save_new
            def broken(file,value):
                if file.name=='result.json': raise OSError('injected persistence failure')
                return original(file,value)
            with patch.object(supervision,'_save_new',broken),self.assertRaises(Refusal):
                supervise_rotation_once(path,MANIFEST,proposal_admission(path),backend,
                    source_commit=SOURCE,interpreter=sys.executable,owner='daisy',monotonic=clock)
            self.assertTrue((path/'reservation.json').exists())
            self.assertTrue(backend.handle.stopped)


if __name__=='__main__': unittest.main()
