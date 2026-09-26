"""Small atomic held/completed handshake; no FEM imports or launch authority."""
import json
import os
from pathlib import Path
import time

from .prototype import Refusal


def publish(path, value):
    """Publish a complete message without replacing an existing message."""
    path = Path(path)
    temporary = path.with_name(path.name + '.writing')
    with temporary.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, allow_nan=False, sort_keys=True)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.link(temporary, path)
    temporary.unlink()


def read(path):
    path = Path(path)
    if path.stat().st_size > 8192:
        raise Refusal('oversized handshake')
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise Refusal('handshake must be an object')
    return value


def await_message(path, seconds):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if Path(path).exists():
            return read(path)
        time.sleep(.02)
    raise Refusal('held worker handshake deadline exceeded')


def held(directory, reservation, cgroup, source_binding=None):
    environment = {key: os.environ.get(key) for key in
                   ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
                    'NUMEXPR_NUM_THREADS')}
    publish(directory/'held.json', dict(pid=os.getpid(), cgroup=cgroup,
                                        nonce=reservation['release_nonce'],
                                        threads=environment, source_binding=source_binding))
    release = await_message(directory/'release.json', 15)
    if (release != dict(nonce=reservation['release_nonce'], cgroup=cgroup)
            or cgroup == '/' or not cgroup.startswith('/')
            or any(v != '1' for v in environment.values())):
        raise Refusal('worker release, cgroup or thread identity mismatch')


def completed(directory, reservation):
    """Retain counters until the controller samples them; then actually exit."""
    publish(directory/'finished.json', dict(nonce=reservation['release_nonce']))
    if await_message(directory/'exit.json', 15) != dict(nonce=reservation['release_nonce']):
        raise Refusal('completion acknowledgement mismatch')
