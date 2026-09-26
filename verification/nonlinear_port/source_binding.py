"""Bind held worker source and executable before numerical imports.

Git checks spawn only inside the managed worker cgroup. The owning checkout
must remain unchanged throughout a run; this is not a hostile-writer sandbox.
"""
import hashlib
from pathlib import Path
import re
import subprocess
import sys

from .prototype import Refusal


def expected_binding(root, reservation, interpreter):
    commit = reservation.get('source_commit', '')
    if (not isinstance(commit, str) or not re.fullmatch('[0-9a-f]{40}', commit)
            or reservation.get('interpreter') != interpreter
            or not Path(interpreter).is_absolute()):
        raise Refusal('missing exact source/interpreter reservation')
    binary = Path(interpreter).resolve(strict=True)
    return dict(source_commit=commit, root=str(Path(root).resolve()), clean=True,
                interpreter=interpreter, executable=str(binary),
                executable_sha256=hashlib.sha256(binary.read_bytes()).hexdigest())


def verify_source(reservation):
    root = Path(__file__).resolve().parents[2]
    expected = expected_binding(root, reservation, sys.executable)
    if Path.cwd().resolve() != root:
        raise Refusal('worker cwd differs from loaded source root')
    def git(*args):
        result = subprocess.run(['/usr/bin/git', '-C', str(root), *args],
                                capture_output=True, text=True, timeout=2)
        if result.returncode:
            raise Refusal('worker Git binding check failed')
        return result.stdout.strip()
    if (git('rev-parse', '--show-toplevel') != str(root)
            or git('rev-parse', 'HEAD') != expected['source_commit']
            or git('status', '--porcelain', '--untracked-files=all')):
        raise Refusal('executed checkout does not match clean reserved source')
    return expected
