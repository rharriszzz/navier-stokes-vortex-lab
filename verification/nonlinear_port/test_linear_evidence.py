"""Exercise bounded serialization and failure preservation without FEM imports."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from . import linear_evidence as evidence
from .prototype import Refusal
from .sparse import CSR


class LinearEvidenceChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.writer = evidence.LatestSystem(self.directory, dict(
            source_commit='a'*40, executable_sha256='b'*64))
        self.matrix = CSR.from_rows([{0: 1.}, {1: 0., 2: -1.}, {1: 1.}, {3: 2.}])
        self.args = dict(state=[2., 0., 0., 0.], scales=[1., .5, 1., 1.],
                         fixed={0: 2.}, step=1, correction=1)

    def save(self, **updates):
        return self.writer(self.matrix, [0., 1., 2., 3.], **(self.args | updates))

    def test_exact_sparse_roundtrip_and_atomic_latest_replacement(self):
        original = (self.matrix, dict(self.args))
        first = self.save()
        path = self.directory/'linear_system.json'
        raw = path.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), first['sha256'])
        self.assertEqual(len(raw), first['bytes'])
        data = json.loads(raw)
        self.assertEqual(data['csr'], dict(indptr=list(self.matrix.indptr),
                                          indices=list(self.matrix.indices),
                                          values=list(self.matrix.values)))
        self.assertEqual(data['rhs'], [0., 1., 2., 3.])
        self.assertEqual(data['fixed_indices'], [0])
        self.assertEqual(data['state'], self.args['state'])
        self.assertIsNone(data['factor_permutation'])
        second = self.save(correction=2)
        self.assertNotEqual(first['sha256'], second['sha256'])
        self.assertEqual(json.loads(path.read_bytes())['correction'], 2)
        self.assertEqual(list(self.directory.iterdir()), [path])
        self.assertEqual((self.matrix, self.args), original)

    def test_invalid_vectors_indices_correction_and_caps_refuse_before_write(self):
        for updates in (dict(state=[2., float('nan'), 0., 0.]),
                        dict(scales=[1., 0., 1., 1.]), dict(fixed={1: 0.}),
                        dict(state=[3., 0., 0., 0.]), dict(correction=2),
                        dict(step=2), dict(state=[2.])):
            with self.subTest(updates=updates), self.assertRaises(Refusal):
                self.save(**updates)
        for key, value in (('MAX_DOFS', 3), ('MAX_NNZ', 1), ('MAX_BYTES', 10)):
            with self.subTest(cap=key), patch.object(evidence, key, value), self.assertRaises(Refusal):
                self.save()
        self.assertEqual(list(self.directory.iterdir()), [])
        self.assertEqual(self.writer.last_correction, 0)

    def test_failed_replace_retains_previous_complete_and_partial_file(self):
        self.save()
        path = self.directory/'linear_system.json'
        previous = path.read_bytes()
        with patch.object(evidence.os, 'replace', side_effect=OSError('scripted write failure')):
            with self.assertRaisesRegex(OSError, 'scripted write failure'):
                self.save(correction=2)
        self.assertEqual(path.read_bytes(), previous)
        self.assertTrue((self.directory/'linear_system.json.writing').is_file())
        self.assertEqual(self.writer.last_correction, 1)

    def test_nonfinite_rhs_and_malformed_csr_preserve_previous(self):
        self.save()
        path = self.directory/'linear_system.json'
        previous = path.read_bytes()
        with self.assertRaises(Refusal):
            self.writer(self.matrix, [0., float('inf'), 2., 3.],
                        **(self.args | dict(correction=2)))
        self.matrix = CSR(4, (0, 2, 1, 3, 4), (0, 1, 2, 3), (1., 1., 1., 1.))
        with self.assertRaises(Refusal):
            self.save(correction=2)
        self.assertEqual(path.read_bytes(), previous)


if __name__ == '__main__':
    unittest.main()
