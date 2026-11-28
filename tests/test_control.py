# Purpose: Test process control signals, process identity, and permission handling.
# Requirements: psutil
# Run: python3 -m unittest discover -s tests -p "test_control.py" -v

import os
import sys
import time
import unittest
import subprocess
from unittest.mock import patch

import psutil

from core.process_control import terminate, suspend, resume


class TestProcessControl(unittest.TestCase):

    def setUp(self):
        self.worker = subprocess.Popen([
            sys.executable,
            "-c",
            "import time; time.sleep(60)"
        ])

        self.pid = self.worker.pid
        self.create_time = psutil.Process(self.pid).create_time()

    def tearDown(self):
        if self.worker.poll() is None:
            self.worker.kill()
            self.worker.wait()

    def wait_for_status(self, expected, timeout=3):
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            try:
                if psutil.Process(self.pid).status() == expected:
                    return True
            except psutil.NoSuchProcess:
                return False

            time.sleep(0.05)

        return False

    def test_suspend(self):
        result = suspend(self.pid, self.create_time)

        self.assertTrue(result["success"])
        self.assertTrue(
            self.wait_for_status(psutil.STATUS_STOPPED)
        )

    def test_resume(self):
        suspend_result = suspend(self.pid, self.create_time)

        self.assertTrue(suspend_result["success"])
        self.assertTrue(
            self.wait_for_status(psutil.STATUS_STOPPED)
        )

        resume_result = resume(self.pid, self.create_time)

        self.assertTrue(resume_result["success"])
        self.assertTrue(self.wait_until_resumed())


    def test_terminate(self):
        result = terminate(self.pid, self.create_time)

        self.assertTrue(result["success"])
        self.worker.wait(timeout=5)

        self.assertIsNotNone(self.worker.poll())

    def test_nonexistent_process(self):
        with patch(
            "core.process_control.psutil.Process",
            side_effect=psutil.NoSuchProcess(99999999)
        ):
            result = terminate(99999999, 1700000000.0)

        self.assertFalse(result["success"])

    def test_protect_application(self):
        pid = os.getpid()
        create_time = psutil.Process(pid).create_time()

        result = terminate(pid, create_time)

        self.assertFalse(result["success"])

    def test_create_time_mismatch(self):
        result = suspend(
            self.pid,
            self.create_time + 100
        )

        self.assertFalse(result["success"])

    def test_access_denied(self):
        with patch(
            "core.process_control.psutil.Process",
            side_effect=psutil.AccessDenied(self.pid)
        ):
            result = terminate(self.pid, self.create_time)

        self.assertFalse(result["success"])

    def wait_until_resumed(self, timeout=3):
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            try:
                process = psutil.Process(self.pid)

                if (
                    process.is_running()
                    and process.status() != psutil.STATUS_STOPPED
                ):
                    return True

            except psutil.NoSuchProcess:
                return False

            time.sleep(0.05)

        return False


if __name__ == "__main__":
    unittest.main()
