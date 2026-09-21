"""Pure validator for a bounded newline-delimited Windows memory-helper protocol."""
from __future__ import annotations

import json

from monitor_core import HostReading, MonitorError, _integer, _number

MAX_LINE_BYTES = 4096
MAX_PENDING = 1


class HostProtocol:
    def __init__(self, *, nonce: str, clock, max_line_bytes: int = MAX_LINE_BYTES):
        if not isinstance(nonce, str) or not nonce:
            raise MonitorError("run nonce required")
        self.nonce = nonce
        self.clock = clock
        self.max_line_bytes = _integer("max line bytes", max_line_bytes, minimum=32)
        self.pending: tuple[int, float] | None = None
        self.last_request = None
        self.last_sequence = 0
        self.last_request_send = None

    def request(self, sequence: int, send_time: float) -> bytes:
        sequence = _integer("request sequence", sequence, minimum=1)
        sent = _number("request send time", send_time)
        if self.pending is not None or sequence != self.last_sequence + 1:
            raise MonitorError("duplicate/out-of-order request or request already pending")
        self.pending = (sequence, sent)
        self.last_sequence = sequence
        self.last_request_send = sent
        payload = {"schema": 1, "sequence": sequence, "nonce": self.nonce, "operation": "memory"}
        return (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")

    def reply(self, line: bytes, receipt_time: float) -> HostReading:
        receipt = _number("reply receipt time", receipt_time)
        if self.pending is None:
            raise MonitorError("unsolicited host reply")
        if not isinstance(line, bytes) or len(line) > self.max_line_bytes or not line.endswith(b"\n"):
            raise MonitorError("host reply length or framing invalid")
        sequence, sent = self.pending
        try:
            value = json.loads(line[:-1].decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise MonitorError("malformed host reply") from exc
        if (not isinstance(value, dict) or type(value.get("schema")) is not int or
                value.get("schema") != 1):
            raise MonitorError("host reply schema invalid")
        if (type(value.get("sequence")) is not int or value.get("sequence") != sequence or
                value.get("nonce") != self.nonce):
            raise MonitorError("host reply sequence/nonce mismatch")
        status = value.get("status")
        error = value.get("error")
        available = value.get("available_bytes")
        total = value.get("total_bytes")
        if status != "ok":
            self.pending = None
            return HostReading(sequence, sent, receipt, "windows", "error", None, None,
                               str(error or "native memory API failed"))
        available = _integer("available physical bytes", available)
        total = _integer("total physical bytes", total, minimum=1)
        if available > total or receipt < sent or receipt - sent >= 0.5:
            raise MonitorError("host reply values or request deadline invalid")
        if self.last_request is not None and receipt - self.last_request > 1.0:
            raise MonitorError("host reply receipt gap exceeds one second")
        self.last_request = sent
        self.pending = None
        return HostReading(sequence, sent, receipt, "windows", "ok", available, total)

    def expired(self, now: float) -> bool:
        """True at the conservative request-send + 0.5 s response deadline."""
        current = _number("host protocol clock", now)
        return self.pending is not None and current >= self.pending[1] + 0.5
