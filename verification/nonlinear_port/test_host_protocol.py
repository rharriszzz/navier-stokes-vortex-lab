"""Standard-library protocol regressions. These do not certify a live backend."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from .handshake import publish, read, held, completed
from .prototype import Refusal
from .systemd_backend import Handle, seconds
from .test_driver_supervision import (Clock, FakeBackend, FakeHandle,
                                      MANIFEST, SOURCE, admission)
from .supervision import supervise_once
from . import supervision


class HostProtocol(unittest.TestCase):
    def test_atomic_handshake_and_wrong_nonce_refusal(self):
        with TemporaryDirectory() as base:
            path = Path(base)
            publish(path/'release.json', {'nonce': 'wrong', 'cgroup': '/test'})
            with self.assertRaises(FileExistsError):
                publish(path/'release.json', {'nonce': 'correct', 'cgroup': '/test'})
            self.assertEqual(read(path/'release.json')['nonce'], 'wrong')
            with self.assertRaises(Refusal):
                held(path, {'release_nonce': 'correct'}, '/test')

    def test_completed_worker_rejects_wrong_ack(self):
        with TemporaryDirectory() as base:
            path = Path(base)
            publish(path/'exit.json', {'nonce': 'wrong'})
            with self.assertRaises(Refusal):
                completed(path, {'release_nonce': 'right'})

    def test_manager_duration_format_at_real_runtime_limit(self):
        self.assertEqual(seconds('2min 29s'), 149)
        self.assertEqual(seconds('1s'), 1)
        self.assertEqual(seconds('500ms'), .5)
        for value in ('infinity', '-1s', '149', 'garbage'):
            with self.assertRaises(Refusal):
                seconds(value)

    def test_active_exited_service_retains_actual_exit(self):
        with TemporaryDirectory() as base:
            path = Path(base)
            publish(path/'reservation.json', {'release_nonce': 'n'})
            publish(path/'finished.json', {'nonce': 'n'})
            h = Handle(path, path, 149)
            with (patch.object(h, 'snapshot', return_value={'memory_peak_bytes': 1000}),
                  patch.object(h, 'show', return_value={
                    'ActiveState': 'active', 'SubState': 'exited', 'MainPID': '0',
                    'ExecMainCode': '1', 'ExecMainStatus': '0', 'Result': 'success'})):
                self.assertEqual(h.wait(1)['exit_code'], 0)
            self.assertTrue((path/'resource_snapshot.json').exists())
            self.assertTrue((path/'exit.json').exists())

    def test_disappeared_service_cleanup_does_not_stop_unknown_unit(self):
        with TemporaryDirectory() as base:
            path = Path(base)
            publish(path/'reservation.json', {'release_nonce': 'n'})
            h = Handle(path, path, 149)
            with (patch.object(h, 'show', return_value={
                    'LoadState': 'not-found', 'ActiveState': 'inactive', 'MainPID': '0'}),
                  patch.object(h, 'connection') as command):
                h.stop()
                self.assertTrue(h.cleanup()['empty'])
                command.assert_not_called()

    def test_partial_start_still_cleans_known_handle(self):
        class Partial(FakeBackend):
            def start_held(self, command, directory, caps):
                self.active_handle = FakeHandle(directory, self.clock)
                raise Refusal('held handshake failed after service creation')
        with TemporaryDirectory() as base:
            path = Path(base)/'run'
            clock = Clock()
            backend = Partial(clock)
            result = supervise_once(path, MANIFEST, admission(path), backend,
                                    source_commit=SOURCE, interpreter='python',
                                    owner='daisy', monotonic=clock)
            self.assertTrue(backend.active_handle.stopped)
            self.assertEqual(result['status'], 'INCOMPLETE')
            self.assertTrue(result['cleanup']['empty'])

    def test_resource_limit_events_refuse_even_without_oom_kill(self):
        for field in ('memory_events', 'pids_events'):
            original = FakeHandle.cleanup
            def cleanup(h):
                result = original(h)
                result[field]['max'] = 1
                return result
            with TemporaryDirectory() as base, patch.object(FakeHandle, 'cleanup', cleanup):
                path = Path(base)/'run'
                clock = Clock()
                result = supervise_once(path, MANIFEST, admission(path), FakeBackend(clock),
                                        source_commit=SOURCE, interpreter='python',
                                        owner='daisy', monotonic=clock)
                self.assertEqual(result['status'], 'INCOMPLETE')

    def test_completion_save_tail_cannot_exceed_finish_subdeadline(self):
        with TemporaryDirectory() as base:
            path = Path(base)/'run'
            clock = Clock()
            original = supervision._save_new
            def save(file, value):
                original(file, value)
                if file.name == 'completion.json':
                    clock.value += 16
            with patch.object(supervision, '_save_new', save):
                result = supervise_once(path, MANIFEST, admission(path), FakeBackend(clock),
                                        source_commit=SOURCE, interpreter='python',
                                        owner='daisy', monotonic=clock)
            self.assertLess(clock(), 180)
            self.assertEqual(result['status'], 'INCOMPLETE')
            self.assertTrue((path/'late.json').exists())


if __name__ == '__main__':
    unittest.main()
