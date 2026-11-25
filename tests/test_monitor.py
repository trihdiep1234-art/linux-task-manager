# Run: PYTHONPATH=. python3 -m unittest discover -s tests -p "test_monitor.py" -v

import os
import time
import unittest
import psutil
from core.models import ProcessInfo
from core.proc_reader import read_proc_status
from core.process_monitor import ProcessMonitor

class TestProcessMonitor(unittest.TestCase):
    # Verify the data retrieval flow and CPU% calculation interval
    def test_structure_and_cpu_sampling(self) -> None:
        monitor = ProcessMonitor()
        first_snapshot = monitor.get_processes()
        self.assertGreater(len(first_snapshot), 0)
        for proc in first_snapshot:
            self.assertIsInstance(proc, ProcessInfo)
            self.assertIsNone(proc.cpu_percent)
            self.assertGreaterEqual(proc.rss_bytes, 0)
        time.sleep(0.5)
        second_snapshot = monitor.get_processes()
        sampled_count = sum(1 for p in second_snapshot if p.cpu_percent is not None)
        self.assertGreater(sampled_count, 0)
# Handle exceptions when processes disappear
    def test_non_existent_pid(self) -> None:
        result = read_proc_status(9999999)
        self.assertIsNone(result)
# Cross-validate data from /proc and psutil
    def test_cross_check(self) -> None:
        current_pid = os.getpid()
        proc_data = read_proc_status(current_pid)
        ps_proc = psutil.Process(current_pid)

        self.assertIsNotNone(proc_data)
        assert proc_data is not None
        self.assertEqual(proc_data["pid"], ps_proc.pid)
        self.assertEqual(proc_data["ppid"], ps_proc.ppid())
        self.assertEqual(proc_data["name"], ps_proc.name())
        self.assertEqual(proc_data["num_threads"], ps_proc.num_threads())

if __name__ == "__main__":
    unittest.main()