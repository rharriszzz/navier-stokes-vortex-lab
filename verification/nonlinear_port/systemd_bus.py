"""Finite in-process sd-bus client; no systemctl/systemd-run helper processes.

Uses the installed libsystemd C ABI (v249), only fixed-argument functions.
The pre-existing caller and OS manager are the R103 trusted control boundary.
"""
import ctypes as C
from contextlib import contextmanager
import os
import socket
import struct

from .prototype import Refusal


class BusError(Refusal):
    def __init__(self, name, message):
        self.name = name
        super().__init__(name + ': ' + message)


class Error(C.Structure):
    _fields_ = [('name', C.c_char_p), ('message', C.c_char_p), ('need_free', C.c_int)]


class Bus:
    destination = b'org.freedesktop.systemd1'
    manager = b'org.freedesktop.systemd1.Manager'
    path = b'/org/freedesktop/systemd1'

    def __init__(self):
        self.lib = C.CDLL('libsystemd.so.0')
        p, s, char = C.c_void_p, C.c_char_p, C.c_char
        signatures = {
            'sd_bus_new': (C.c_int, [C.POINTER(p)]),
            'sd_bus_set_address': (C.c_int, [p, s]),
            'sd_bus_start': (C.c_int, [p]),
            'sd_bus_get_fd': (C.c_int, [p]),
            'sd_bus_close_unref': (p, [p]),
            'sd_bus_message_unref': (p, [p]),
            'sd_bus_error_free': (C.POINTER(Error), [C.POINTER(Error)]),
            'sd_bus_message_new_method_call': (C.c_int, [p, C.POINTER(p), s, s, s, s]),
            'sd_bus_message_append_basic': (C.c_int, [p, char, p]),
            'sd_bus_message_open_container': (C.c_int, [p, char, s]),
            'sd_bus_message_close_container': (C.c_int, [p]),
            'sd_bus_message_enter_container': (C.c_int, [p, char, s]),
            'sd_bus_message_read_basic': (C.c_int, [p, char, p]),
            'sd_bus_call': (C.c_int, [p, p, C.c_uint64, C.POINTER(Error), C.POINTER(p)]),
        }
        for name, (restype, args) in signatures.items():
            fn = getattr(self.lib, name)
            fn.restype, fn.argtypes = restype, args
        self.bus = p()
        self.check(self.lib.sd_bus_new(C.byref(self.bus)))
        try:
            address = f'unix:path=/run/user/{os.geteuid()}/systemd/private'.encode()
            self.check(self.lib.sd_bus_set_address(self.bus, address))
            self.check(self.lib.sd_bus_start(self.bus))
            fd = self.check(self.lib.sd_bus_get_fd(self.bus))
            with socket.fromfd(fd, socket.AF_UNIX, socket.SOCK_STREAM) as peer:
                _, uid, _ = struct.unpack('3i', peer.getsockopt(socket.SOL_SOCKET,
                                                               socket.SO_PEERCRED, 12))
                if uid not in (0, os.geteuid()):
                    raise Refusal('unexpected systemd manager peer')
        except BaseException:
            self.close()
            raise

    @staticmethod
    def check(result):
        if result < 0:
            raise Refusal('sd-bus operation failed: errno ' + str(-result))
        return result

    def close(self):
        if self.bus:
            self.lib.sd_bus_close_unref(self.bus)
            self.bus = C.c_void_p()

    @contextmanager
    def message(self, member, *, path=None, interface=None):
        msg = C.c_void_p()
        self.check(self.lib.sd_bus_message_new_method_call(
            self.bus, C.byref(msg), self.destination, path or self.path,
            interface or self.manager, member.encode()))
        try:
            yield msg
        finally:
            self.lib.sd_bus_message_unref(msg)

    @contextmanager
    def container(self, msg, kind, signature):
        self.check(self.lib.sd_bus_message_open_container(msg, kind.encode(), signature.encode()))
        yield
        self.check(self.lib.sd_bus_message_close_container(msg))

    def append(self, msg, kind, value):
        if kind in ('s', 'o'):
            if '\0' in value:
                raise Refusal('NUL in D-Bus string')
            pointer = C.c_char_p(value.encode())
        else:
            number = {'b': C.c_int, 't': C.c_uint64}[kind](value)
            pointer = C.byref(number)
        self.check(self.lib.sd_bus_message_append_basic(msg, kind.encode(), pointer))

    def strings(self, msg, values):
        with self.container(msg, 'a', 's'):
            for value in values:
                self.append(msg, 's', value)

    @contextmanager
    def call(self, msg):
        reply, error = C.c_void_p(), Error()
        try:
            result = self.lib.sd_bus_call(self.bus, msg, 1_000_000, C.byref(error), C.byref(reply))
            if result < 0:
                raise BusError((error.name or b'unknown').decode(),
                               (error.message or str(-result).encode()).decode())
            yield reply
        finally:
            self.lib.sd_bus_error_free(C.byref(error))
            if reply:
                self.lib.sd_bus_message_unref(reply)

    def read(self, msg, kind):
        value = {'s': C.c_char_p, 'o': C.c_char_p, 'b': C.c_int,
                 'i': C.c_int32, 'u': C.c_uint32, 't': C.c_uint64}[kind]()
        if self.check(self.lib.sd_bus_message_read_basic(msg, kind.encode(), C.byref(value))) != 1:
            raise Refusal('missing D-Bus value')
        return value.value.decode() if kind in ('s', 'o') else value.value

    def unit_path(self, unit):
        with self.message('GetUnit') as msg:
            self.append(msg, 's', unit)
            with self.call(msg) as reply:
                return self.read(reply, 'o').encode()

    def property(self, path, interface, name, kind):
        with self.message('Get', path=path, interface=b'org.freedesktop.DBus.Properties') as msg:
            self.append(msg, 's', 'org.freedesktop.systemd1.' + interface)
            self.append(msg, 's', name)
            with self.call(msg) as reply:
                if self.check(self.lib.sd_bus_message_enter_container(reply, b'v', kind.encode())) != 1:
                    raise Refusal('missing D-Bus variant')
                return self.read(reply, kind)

    def start(self, unit, properties, argv):
        with self.message('StartTransientUnit') as msg:
            self.append(msg, 's', unit)
            self.append(msg, 's', 'fail')
            with self.container(msg, 'a', '(sv)'):
                for name, kind, value in properties:
                    with self.container(msg, 'r', 'sv'):
                        self.append(msg, 's', name)
                        with self.container(msg, 'v', kind):
                            if kind == 'as':
                                self.strings(msg, value)
                            else:
                                self.append(msg, kind, value)
                with self.container(msg, 'r', 'sv'):
                    self.append(msg, 's', 'ExecStart')
                    with self.container(msg, 'v', 'a(sasb)'):
                        with self.container(msg, 'a', '(sasb)'):
                            with self.container(msg, 'r', 'sasb'):
                                self.append(msg, 's', argv[0])
                                self.strings(msg, argv)
                                self.append(msg, 'b', False)
            with self.container(msg, 'a', '(sa(sv))'):
                pass
            with self.call(msg) as reply:
                return self.read(reply, 'o')

    def stop(self, unit):
        with self.message('StopUnit') as msg:
            self.append(msg, 's', unit)
            self.append(msg, 's', 'replace')
            with self.call(msg) as reply:
                return self.read(reply, 'o')
