import time
import psutil
from core.models import ProcessInfo
from core.proc_reader import read_proc_status
# Combine two data sources: /proc/[pid]/status provides process identification and status information,
# psutil calculates CPU% and maps usernames.

class ProcessMonitor:
    def __init__(self) -> None:
        self._proc_cache: dict[tuple[int, float], psutil.Process] = {}

    def get_processes(self) -> list[ProcessInfo]:
        processes: list[ProcessInfo] = []
        active_keys: set[tuple[int, float]] = set()

        for proc in psutil.process_iter(["pid", "create_time", "username"]):
            try:
                pid = proc.info["pid"]
                create_time = proc.info["create_time"]
                if pid is None or create_time is None:
                    continue

                proc_data = read_proc_status(pid)
                if proc_data is None:
                    continue

                key = (pid, create_time)
                active_keys.add(key)

                if key in self._proc_cache:
                    cached_proc = self._proc_cache[key]
                    cpu_val = cached_proc.cpu_percent(interval=None)
                    cpu_percent: float | None = round(cpu_val, 1)
                else:
                    proc.cpu_percent(interval=None)
                    self._proc_cache[key] = proc
                    cpu_percent = None

                username = proc.info.get("username") or "unknown"

                processes.append(
                    ProcessInfo(
                        pid=int(proc_data["pid"]),
                        create_time=float(create_time),
                        ppid=int(proc_data["ppid"]),
                        name=str(proc_data["name"]),
                        username=str(username),
                        status=str(proc_data["status"]),
                        cpu_percent=cpu_percent,
                        rss_bytes=int(proc_data["rss_bytes"]),
                        num_threads=int(proc_data["num_threads"]),
                    )
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        stale_keys = set(self._proc_cache.keys()) - active_keys
        for key in stale_keys:
            del self._proc_cache[key]

        return processes

_default_monitor = ProcessMonitor()

def get_processes() -> list[ProcessInfo]:
    return _default_monitor.get_processes()

if __name__ == "__main__":
    print("Lan quet 1 (khoi tao moc CPU%):")
    first_batch = get_processes()
    print(f"Tong so tien trinh: {len(first_batch)}")
    for p in first_batch[:5]:
        print(p)

    time.sleep(2)

    print("\nLan quet 2 (sau 2 giay - da co CPU%):")
    second_batch = get_processes()
    top_cpu = sorted(
        second_batch,
        key=lambda x: x.cpu_percent if x.cpu_percent is not None else -1.0,
        reverse=True,
    )[:5]
    for p in top_cpu:
        print(p)