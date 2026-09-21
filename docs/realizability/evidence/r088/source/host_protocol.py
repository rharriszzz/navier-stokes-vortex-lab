"""Pure validator for a bounded newline-delimited Windows memory-helper protocol."""
from __future__ import annotations

import json

from primitives import HostReading, MonitorError, _integer, _number

MAX_LINE_BYTES = 4096
MAX_PENDING = 1


def _object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise MonitorError("duplicate JSON key")
        value[key] = item
    return value


def _constant(_value):
    raise MonitorError("non-finite JSON constant")


class HostProtocol:
    def __init__(self, *, nonce: str, clock, max_line_bytes: int = MAX_LINE_BYTES):
        if not isinstance(nonce, str) or not nonce:
            raise MonitorError("run nonce required")
        self.nonce = nonce
        self.clock = clock
        if type(max_line_bytes) is not int or max_line_bytes != MAX_LINE_BYTES:
            raise MonitorError("protocol framing bound is fixed at 4096 bytes")
        self.max_line_bytes = MAX_LINE_BYTES
        self.last_time = None
        self.last_receipt = None
        self.pending: tuple[int, float] | None = None
        self.last_request = None
        self.last_sequence = 0
        self.last_request_send = None
        self.provider_identity = None
        self.terminal_error: str | None = None
        self.buffer = bytearray()

    def check_time(self, value):
        current = _number("protocol time", value)
        if self.last_time is not None and current < self.last_time:
            raise MonitorError("protocol clock regressed")
        self.last_time = current
        return current

    def fail(self, error):
        self.terminal_error = str(error)
        self.buffer.clear()
        self.pending = None

    def request(self, sequence: int, send_time: float) -> bytes:
        try:
            if self.terminal_error is not None:
                raise MonitorError("host protocol is terminal")
            sequence = _integer("request sequence", sequence, minimum=1)
            sent = self.check_time(send_time)
            if self.pending is not None or sequence != self.last_sequence + 1:
                raise MonitorError("duplicate/out-of-order request or request already pending")
            if self.last_request is not None and sent - self.last_request > 1.0:
                raise MonitorError("previous host baseline stale")
            self.pending = (sequence, sent)
            self.last_sequence = sequence
            self.last_request_send = sent
            payload = {"schema": 1, "sequence": sequence, "nonce": self.nonce, "operation": "memory"}
            return (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
        except BaseException as exc:
            self.fail(exc)
            raise

    def _reply(self, line: bytes, receipt_time: float) -> HostReading:
        receipt = self.check_time(receipt_time)
        if self.pending is None:
            raise MonitorError("unsolicited host reply")
        if not isinstance(line, bytes) or len(line) > self.max_line_bytes or not line.endswith(b"\n"):
            raise MonitorError("host reply length or framing invalid")
        sequence, sent = self.pending
        try:
            value = json.loads(line[:-1].decode("utf-8"), object_pairs_hook=_object,
                               parse_constant=_constant)
        except (UnicodeDecodeError, json.JSONDecodeError, MonitorError) as exc:
            raise MonitorError("malformed host reply") from exc
        if (not isinstance(value, dict) or type(value.get("schema")) is not int or
                value.get("schema") != 1):
            raise MonitorError("host reply schema invalid")
        if set(value) != {"schema", "sequence", "nonce", "status", "available_bytes",
                          "total_bytes", "error", "provider_pid", "provider_created"}:
            raise MonitorError("host reply fields differ from protocol schema")
        if (type(value.get("sequence")) is not int or value.get("sequence") != sequence or
                value.get("nonce") != self.nonce):
            raise MonitorError("host reply sequence/nonce mismatch")
        status = value.get("status")
        provider_pid = _integer("host provider PID", value.get("provider_pid"), minimum=1)
        provider_created = _integer("host provider creation identity", value.get("provider_created"), minimum=1)
        provider_identity = (provider_pid, provider_created)
        if self.provider_identity is not None and provider_identity != self.provider_identity:
            raise MonitorError("host provider identity changed within session")
        error = value.get("error")
        available = value.get("available_bytes")
        total = value.get("total_bytes")
        if status != "ok":
            if (status != "error" or not isinstance(error, str) or not error or
                    available is not None or total is not None):
                raise MonitorError("contradictory host failure fields")
            self.pending = None
            self.provider_identity = provider_identity
            return HostReading(sequence, sent, receipt, "windows", "error", None, None,
                               error, self.nonce, provider_pid, provider_created)
        if error is not None:
            raise MonitorError("successful host reply includes an API error")
        available = _integer("available physical bytes", available)
        total = _integer("total physical bytes", total, minimum=1)
        if available > total or receipt < sent or receipt - sent >= 0.5:
            raise MonitorError("host reply values or request deadline invalid")
        if self.last_request is not None and receipt - self.last_request > 1.0:
            raise MonitorError("host reply receipt gap exceeds one second")
        self.last_receipt = receipt
        self.last_request = sent
        self.provider_identity = provider_identity
        self.pending = None
        return HostReading(sequence, sent, receipt, "windows", "ok", available, total,
                           None, self.nonce, provider_pid, provider_created)

    def reply(self, line: bytes, receipt_time: float) -> HostReading:
        if self.terminal_error is not None:
            raise MonitorError("host protocol is terminal")
        try:
            reading = self._reply(line, receipt_time)
        except BaseException as exc:
            self.fail(f"{type(exc).__name__}: {exc}")
            raise
        if reading.status != "ok":
            self.terminal_error = "host API reported failure"
        return reading

    def feed(self, chunk: bytes, receipt_time: float, *, eof: bool = False) -> HostReading | None:
        """Consume bounded incremental bytes; every framing/EOF fault is terminal."""
        if self.terminal_error is not None:
            raise MonitorError("host protocol is terminal")
        if eof:
            self.terminal_error = "host transport reached EOF"
            self.buffer.clear()
            raise MonitorError(self.terminal_error)
        if not isinstance(chunk, bytes) or len(self.buffer) + len(chunk) > self.max_line_bytes:
            self.terminal_error = "host input overflow or non-bytes input"
            self.buffer.clear()
            raise MonitorError(self.terminal_error)
        self.buffer.extend(chunk)
        newline = self.buffer.find(b"\n")
        if newline < 0:
            return None
        if newline != len(self.buffer) - 1:
            self.terminal_error = "multiple or trailing host frames"
            self.buffer.clear()
            raise MonitorError(self.terminal_error)
        line = bytes(self.buffer)
        self.buffer.clear()
        try:
            return self.reply(line, receipt_time)
        except BaseException:
            self.terminal_error = self.terminal_error or "host frame rejected"
            raise

    def expired(self, now: float) -> bool:
        try:
            if self.terminal_error is not None:
                return True
            current = self.check_time(now)
            expired = ((self.pending is not None and current >= self.pending[1] + 0.5)
                       or (self.last_request is not None and current - self.last_request > 1.0))
            if expired:
                self.fail("host request or baseline timed out")
            return expired
        except BaseException as exc:
            self.fail(exc)
            raise
