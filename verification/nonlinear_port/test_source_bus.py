"""Binding and manager-failure regressions without launching a service."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import sys
import unittest
from unittest.mock import Mock, patch

from .handshake import publish
from .prototype import Refusal
from .source_binding import expected_binding, verify_source
from .systemd_backend import Handle
from .systemd_bus import Bus, BusError


ROOT = Path(__file__).resolve().parents[2]
RESERVATION = dict(source_commit='a'*40, interpreter=sys.executable, release_nonce='test')


class BindingAndBus(unittest.TestCase):
    def test_worker_observes_clean_source_and_actual_binary(self):
        outputs = [str(ROOT), 'a'*40, '']
        with patch('verification.nonlinear_port.source_binding.subprocess.run',
                   side_effect=[SimpleNamespace(returncode=0, stdout=v) for v in outputs]) as run:
            actual = verify_source(RESERVATION)
        self.assertEqual(actual, expected_binding(ROOT, RESERVATION, sys.executable))
        self.assertEqual(len(actual['executable_sha256']), 64)
        self.assertEqual(run.call_count, 3)
        for call in run.call_args_list:
            self.assertEqual(call.kwargs['timeout'], 2)
            self.assertEqual(call.args[0][0], '/usr/bin/git')

    def test_worker_refuses_dirty_wrong_revision_or_git_failure(self):
        for revision, status, code in [('b'*40, '', 0), ('a'*40, ' M worker.py', 0),
                                      ('a'*40, '?? extra.py', 0), ('a'*40, '', 1)]:
            with self.subTest(revision=revision, status=status, code=code):
                replies = [SimpleNamespace(returncode=code, stdout=v)
                           for v in (str(ROOT), revision, status)]
                with patch('verification.nonlinear_port.source_binding.subprocess.run', side_effect=replies):
                    with self.assertRaises(Refusal):
                        verify_source(RESERVATION)

    def test_missing_or_mismatched_reservation_refuses(self):
        for reservation in ({}, dict(RESERVATION, source_commit='z'*40),
                            dict(RESERVATION, interpreter='/wrong/python')):
            with self.assertRaises(Refusal):
                expected_binding(ROOT, reservation, sys.executable)

    def test_unknown_unit_only_for_exact_manager_error(self):
        with TemporaryDirectory() as base:
            path = Path(base)
            publish(path/'reservation.json', RESERVATION)
            handle = Handle(ROOT, path, 149)
            bus = Mock()
            with patch.object(handle, 'connection', return_value=bus):
                bus.unit_path.side_effect = BusError('org.freedesktop.systemd1.NoSuchUnit', 'gone')
                self.assertEqual(handle.show()['LoadState'], 'not-found')
                bus.unit_path.side_effect = BusError('org.freedesktop.DBus.Error.NoReply', 'timeout')
                with self.assertRaises(BusError):
                    handle.show()

    def test_stop_waits_for_actual_cleanup_and_not_just_job_submission(self):
        with TemporaryDirectory() as base:
            path = Path(base)
            publish(path/'reservation.json', RESERVATION)
            handle = Handle(ROOT, path, 149)
            running = dict(LoadState='loaded', ActiveState='active', MainPID='42', ControlGroup='/test')
            gone = dict(LoadState='not-found', ActiveState='inactive', MainPID='0', ControlGroup='')
            bus = Mock()
            with (patch.object(handle, 'connection', return_value=bus),
                  patch.object(handle, 'show', side_effect=[running, running, gone]) as show):
                handle.stop()
            self.assertEqual(show.call_count, 3)
            bus.stop.assert_called_once_with(handle.unit)
            self.assertTrue(handle.stopped)

    def test_message_call_error_frees_error_and_reply(self):
        # Check exceptional lifetime handling without connecting to a manager.
        bus = Bus.__new__(Bus)
        bus.bus = None
        bus.lib = Mock()
        bus.lib.sd_bus_call.return_value = -5
        with self.assertRaises(BusError):
            with bus.call(None):
                self.fail('failed call yielded a reply')
        bus.lib.sd_bus_error_free.assert_called_once()


if __name__ == '__main__':
    unittest.main()
