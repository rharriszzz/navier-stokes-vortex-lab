"""Artifact/runtime refusal checks using synthetic files and modules only."""
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import ModuleType, SimpleNamespace
import sys
import unittest
from unittest.mock import patch

from . import worker
from .package_identity import (FFCX_ARTIFACT, FFCX_RUNTIME, RECOVERY_EVIDENCE,
                               MODULE, METADATA, read_ffcx_artifact, validate_versions)
from .prototype import Refusal
from .supervision import validate_worker_result
from .test_driver_supervision import CONTRACT, payload

ROOT = Path(__file__).resolve().parents[2]/'docs/realizability/evidence/r229'


class PackageIdentityChecks(unittest.TestCase):
    def make_prefix(self, base):
        prefix = Path(base)
        record = prefix/'conda-meta/fenics-ffcx-0.10.1-pyhbc3ee6d_1.json'
        record.parent.mkdir()
        record.write_text(json.dumps(dict(FFCX_ARTIFACT, files=[MODULE, METADATA])))
        for relative, content in ((MODULE, '# synthetic module, never executed\n'),
                                  (METADATA, 'Name: fenics-ffcx\nVersion: 0.10.0\n')):
            path = prefix/relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
        return prefix, record

    def test_exact_artifact_retains_distinct_package_and_runtime_versions(self):
        with TemporaryDirectory() as base:
            prefix, _ = self.make_prefix(base)
            artifact = read_ffcx_artifact(prefix, ROOT)
            self.assertEqual(artifact, payload()['ffcx_artifact'])
            validate_versions(payload()['actual_versions'], CONTRACT['versions'], artifact)
            self.assertEqual(artifact['package']['version'], '0.10.1')
            self.assertEqual(payload()['actual_versions']['ffcx'], '0.10.0')

    def test_wrong_artifact_and_missing_installation_evidence_refused(self):
        for key in FFCX_ARTIFACT:
            with self.subTest(key=key), TemporaryDirectory() as base:
                prefix, record = self.make_prefix(base)
                data = json.loads(record.read_text())
                data[key] = 'wrong'
                record.write_text(json.dumps(data))
                with self.assertRaises(Refusal):
                    read_ffcx_artifact(prefix, ROOT)
        with TemporaryDirectory() as base:
            prefix, record = self.make_prefix(base)
            record.unlink()
            with self.assertRaises(Refusal):
                read_ffcx_artifact(prefix, ROOT)

    def test_missing_changed_recovery_evidence_refused(self):
        with TemporaryDirectory() as base, TemporaryDirectory() as evidence:
            prefix, _ = self.make_prefix(base)
            with self.assertRaises(Refusal):
                read_ffcx_artifact(prefix, evidence)
            for name in RECOVERY_EVIDENCE:
                path = Path(evidence)/name
                path.parent.mkdir(exist_ok=True)
                path.write_text('{}')
            with self.assertRaises(Refusal):
                read_ffcx_artifact(prefix, evidence)

    def test_wrong_embedded_metadata_and_external_symlink_refused(self):
        for text in ('Name: fenics-ffcx\nVersion: 0.10.1\n',
                     'Name: fenics-ffcx\nVersion: 0.10.0\nVersion: 0.10.0\n'):
            with TemporaryDirectory() as base:
                prefix, _ = self.make_prefix(base)
                (prefix/METADATA).write_text(text)
                with self.assertRaises(Refusal):
                    read_ffcx_artifact(prefix, ROOT)
        with TemporaryDirectory() as base, TemporaryDirectory() as outside:
            prefix, _ = self.make_prefix(base)
            other = Path(outside)/'module.py'
            other.write_text('# outside')
            (prefix/MODULE).unlink()
            (prefix/MODULE).symlink_to(other)
            with self.assertRaises(Refusal):
                read_ffcx_artifact(prefix, ROOT)

    def test_result_reader_refuses_wrong_runtime_artifact_and_missing_evidence(self):
        mutations = [
            lambda p: p['actual_versions'].__setitem__('ffcx', '0.10.1'),
            lambda p: p['actual_versions'].__setitem__('ffcx', '0.9.0'),
            lambda p: p['actual_versions'].__setitem__('dolfinx', '0.9.0'),
            lambda p: p.__setitem__('actual_versions', None),
            lambda p: p.pop('ffcx_artifact'),
            lambda p: p.__setitem__('ffcx_artifact', None),
            lambda p: p['ffcx_artifact']['package'].__setitem__('sha256', '0'*64),
            lambda p: p['ffcx_artifact']['package'].__setitem__('build', 'other'),
            lambda p: p['ffcx_artifact'].pop('recovery_evidence'),
        ]
        for mutation in mutations:
            bad = deepcopy(payload())
            mutation(bad)
            with self.subTest(mutation=mutation), self.assertRaises(Refusal):
                validate_worker_result(bad, CONTRACT['versions'], CONTRACT['gates'])

    def fake_modules(self):
        modules = {}
        for name in ('numpy', 'dolfinx', 'dolfinx.fem', 'dolfinx.mesh',
                     'dolfinx.fem.petsc', 'basix', 'basix.ufl', 'ufl', 'ffcx',
                     'petsc4py', 'mpi4py'):
            modules[name] = ModuleType(name)
            modules[name].__version__ = payload()['actual_versions'].get(name)
        for name, module in modules.items():
            if '.' in name:
                parent, child = name.rsplit('.', 1)
                setattr(modules[parent], child, module)
        modules['petsc4py'].PETSc = SimpleNamespace(Sys=SimpleNamespace(getVersion=lambda: (3, 25, 5)))
        modules['mpi4py'].MPI = SimpleNamespace(COMM_WORLD=SimpleNamespace(size=1),
                                              Get_library_version=lambda: 'MPICH 5.0.1')
        modules['ffcx'].__file__ = str(Path('/synthetic-prefix')/MODULE)
        return modules

    def test_worker_uses_shared_gate_and_observed_runtime(self):
        for changed in (None, 'runtime', 'origin', 'artifact'):
            modules = self.fake_modules()
            artifact = deepcopy(payload()['ffcx_artifact'])
            if changed == 'runtime':
                modules['ffcx'].__version__ = '0.10.1'
            if changed == 'origin':
                modules['ffcx'].__file__ = '/outside/ffcx/__init__.py'
            if changed == 'artifact':
                artifact['package']['sha256'] = '0'*64
            with (self.subTest(changed=changed), patch.dict(sys.modules, modules),
                  patch.object(sys, 'prefix', '/synthetic-prefix'),
                  patch.object(sys, 'version_info', (3, 12, 13)),
                  patch.object(worker, 'read_ffcx_artifact', return_value=artifact)):
                if changed:
                    with self.assertRaises(Refusal):
                        worker.load_pinned_modules(CONTRACT['versions'])
                else:
                    _, actual, observed = worker.load_pinned_modules(CONTRACT['versions'])
                    self.assertEqual(actual['ffcx'], FFCX_RUNTIME)
                    self.assertEqual(observed, artifact)

    def test_saved_transaction_binds_exact_ffcx_identity(self):
        records = json.loads((ROOT.parent/'r227/installed_records.json').read_text())
        record, = [r for r in records if r['name'] == 'fenics-ffcx']
        self.assertEqual({k: record[k] for k in FFCX_ARTIFACT}, FFCX_ARTIFACT)
