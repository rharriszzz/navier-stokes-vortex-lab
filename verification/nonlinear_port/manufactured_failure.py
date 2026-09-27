"""Finite failure evidence for the held manufactured worker; no FEM imports."""
from collections import deque
import json
import os
from pathlib import Path


STAGES = (
    'imports', 'recorder_init', 'mesh_and_geometry', 'history_and_lift',
    'primary_forms', 'primary_compilation', 'compatibility_and_initial_system',
    'newton', 'diagnostics_24', 'diagnostics_26', 'return_sampling_and_report',
    'numerical_save', 'completion_handshake',
)
MAX_FRAMES = 32
MAX_WALK = 4096
MAX_BYTES = 32768


def _short(value, limit):
    """Bound text without evaluating frame locals or numerical expressions."""
    return value[:limit]


def _message(exc):
    try:
        original = str(exc)
        return _short(original, 512), False, len(original) > 512
    except Exception:
        return '<exception message unavailable>', True, False


class StageTracker:
    def __init__(self):
        self.directory = None
        self.binding = None
        self.last_begun = None
        self.last_completed = None
        self._active = None
        self._next = 0

    def arm(self, directory, binding):
        """Caller may arm only after reservation, admission and source verification."""
        directory = Path(directory)
        if self.directory is not None or not directory.is_dir() or type(binding) is not dict:
            raise ValueError('manufactured failure record cannot be armed')
        self.directory = directory
        self.binding = dict(binding)

    def mark(self, name, edge):
        if edge == 'begin':
            if self._active is not None or self._next >= len(STAGES) or name != STAGES[self._next]:
                raise ValueError('manufactured stage order changed')
            self._active = name
            self.last_begun = name
        elif edge == 'end':
            if self._active != name:
                raise ValueError('manufactured stage completion changed')
            self._active = None
            self.last_completed = name
            self._next += 1
        else:
            raise ValueError('unknown manufactured stage edge')
        print(f'manufactured stage={name} edge={edge}', flush=True)


def _frames(exc):
    first, last = [], deque(maxlen=24)
    total = 0
    fields_truncated = False
    tb = exc.__traceback__
    while tb is not None and total < MAX_WALK:
        code = tb.tb_frame.f_code
        fields_truncated |= len(code.co_filename) > 512 or len(code.co_name) > 256
        item = dict(file=_short(code.co_filename, 512),
                    function=_short(code.co_name, 256), line=tb.tb_lineno)
        if total < 8:
            first.append(item)
        else:
            last.append(item)
        total += 1
        tb = tb.tb_next
    truncated = total > MAX_FRAMES
    return first + list(last), truncated, tb is not None, fields_truncated


def _record(exc, tracker, message, formatting_failed, message_truncated):
    frames, truncated, walk_unfinished, fields_truncated = _frames(exc)
    kind = _short(type(exc).__name__, 256)
    return dict(schema=1, fixture='manufactured', source_binding=tracker.binding,
                last_begun_stage=tracker.last_begun,
                last_completed_stage=tracker.last_completed,
                exception_type=kind, exception_message=message,
                message_format_failed=formatting_failed,
                message_truncated=message_truncated,
                traceback=frames, frames_truncated=truncated,
                traceback_fields_truncated=fields_truncated,
                traceback_walk_unfinished=walk_unfinished,
                chained_exceptions_omitted=True,
                diagnostic_only=True)


def _encoded(record):
    return (json.dumps(record, ensure_ascii=False, sort_keys=True,
                       separators=(',', ':'), allow_nan=False)+'\n').encode('utf-8')


def save_failure(exc, tracker):
    """Return bounded stderr summary; persist only in an armed reserved directory."""
    message, failed, truncated = _message(exc)
    kind = _short(type(exc).__name__, 256)
    summary = f'{kind}: {message}'
    if tracker.directory is None:
        return summary
    record = _record(exc, tracker, message, failed, truncated)
    blob = _encoded(record)
    while len(blob) > MAX_BYTES and len(record['traceback']) > 1:
        # Keep the deepest observed frame; disclose every omitted frame.
        record['traceback'].pop(0)
        record['frames_truncated'] = True
        blob = _encoded(record)
    if len(blob) > MAX_BYTES:
        raise ValueError('manufactured failure record exceeds byte cap')
    with (tracker.directory/'failure.json').open('xb') as stream:
        stream.write(blob)
        stream.flush()
        os.fsync(stream.fileno())
    return summary
