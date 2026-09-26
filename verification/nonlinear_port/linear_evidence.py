"""Bounded latest linear system evidence; standard library, no solve or assembly."""
import hashlib
import json
from math import isfinite
import os
from pathlib import Path
import re

from .cube_adapter import SUPERLU_OPTIONS, SUPERLU_PREFIX
from .prototype import Refusal

MAX_DOFS = 512
MAX_NNZ = 65536
MAX_BYTES = 4 * 1024 * 1024
MAX_CORRECTIONS = 12


def finite_vector(values, n, name):
    if len(values) != n:
        raise Refusal('linear evidence vector size: ' + name)
    try:
        valid = all(type(v) in (int, float) and isfinite(v) for v in values)
    except OverflowError:
        valid = False
    if not valid:
        raise Refusal('linear evidence nonfinite/invalid vector: ' + name)
    return list(values)


class LatestSystem:
    """Replace one complete record per correction inside the reserved directory.

    A failed write leaves the previous complete record and any partial .writing
    file. No diagnostic failure permits a solve or another numerical attempt.
    """
    def __init__(self, directory, binding, *, fixture='poiseuille'):
        self.directory = Path(directory)
        self.binding = dict(binding)
        if fixture not in ('poiseuille', 'manufactured'):
            raise Refusal('unsupported linear evidence fixture')
        self.fixture = fixture
        if (not self.directory.is_dir()
                or not re.fullmatch('[0-9a-f]{40}', binding.get('source_commit', ''))
                or not re.fullmatch('[0-9a-f]{64}', binding.get('executable_sha256', ''))):
            raise Refusal('linear evidence requires reserved directory and source binding')
        self.last_correction = 0

    def __call__(self, matrix, rhs, *, state, scales, fixed, step, correction):
        n = matrix.n
        if (type(n) is not int or not 4 <= n <= MAX_DOFS
                or len(matrix.values) > MAX_NNZ
                or type(step) is not int or step != 1
                or type(correction) is not int
                or correction != self.last_correction + 1
                or correction > MAX_CORRECTIONS):
            raise Refusal('linear evidence dimension/step/correction cap')
        try:
            matrix.validate(n)
        except (ValueError, OverflowError) as exc:
            raise Refusal('linear evidence invalid CSR') from exc
        rhs = finite_vector(rhs, n, 'rhs')
        state = finite_vector(state, n, 'state')
        scales = finite_vector(scales, n, 'row_scales')
        values = finite_vector(matrix.values, len(matrix.values), 'values')
        if (any(s <= 0 for s in scales) or not fixed
                or any(type(i) is not int or not 0 <= i < n-3 for i in fixed)):
            raise Refusal('linear evidence invalid scales/fixed indices')
        indices = sorted(fixed)
        fixed_values = finite_vector([fixed[i] for i in indices], len(indices), 'fixed_values')
        if any(state[i] != value for i, value in zip(indices, fixed_values)):
            raise Refusal('linear evidence state lost installed lift')
        record = dict(
            schema=1, fixture=self.fixture, subdivisions=2, step=step,
            dt=0.125, correction=correction, stage='before_factorization',
            source_binding=self.binding, shape=[n, n], mixed_dofs=n-3,
            unknown_order='mixed u/p, P_minus, P_plus, eta',
            csr=dict(indptr=matrix.indptr, indices=matrix.indices, values=values),
            rhs=rhs, state=state, row_scales=scales,
            fixed_indices=indices, fixed_values=fixed_values,
            operator='already lifted and row scaled; rhs is negative scaled residual',
            solver=dict(ksp='preonly', pc='lu', backend='superlu', shift='none',
                        options_prefix=SUPERLU_PREFIX, options=dict(SUPERLU_OPTIONS)),
            factor_permutation=None, pivot_coordinate=None,
            caps=dict(dofs=MAX_DOFS, nnz=MAX_NNZ, bytes=MAX_BYTES))
        # Bound serialized output before opening a file, without a dense matrix.
        data = bytearray()
        encoder = json.JSONEncoder(allow_nan=False, sort_keys=True, separators=(',', ':'))
        for chunk in encoder.iterencode(record):
            encoded = chunk.encode('utf-8')
            if len(data) + len(encoded) + 1 > MAX_BYTES:
                raise Refusal('linear evidence serialized byte cap')
            data.extend(encoded)
        data.extend(b'\n')
        temporary = self.directory/'linear_system.json.writing'
        with temporary.open('xb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, self.directory/'linear_system.json')
        self.last_correction = correction
        receipt = dict(file='linear_system.json', correction=correction,
                       sha256=hashlib.sha256(data).hexdigest(), bytes=len(data))
        print('linear system evidence: ' + json.dumps(receipt, sort_keys=True), flush=True)
        return receipt
