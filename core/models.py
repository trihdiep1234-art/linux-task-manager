from dataclasses import dataclass, asdict

# quy dinh cau truc chuan de dong goi thong tin cua 1 tien trinh từ kernel lên gui
@dataclass
class ProcessInfo:  
    pid: int
    create_time: float
    ppid: int
    name: str
    username: str
    status: str
    cpu_percent: float | None
    rss_bytes: int
    num_threads: int

    def to_dict(self) -> dict:
        return asdict(self)

# test voi 3 trang thai S,R,T
def get_mock_processes() -> list[ProcessInfo]:
    return [
        ProcessInfo(
            pid=1,
            create_time=1700000000.0,
            ppid=0,
            name="systemd",
            username="root",
            status="S",
            cpu_percent=0.1,
            rss_bytes=12 * 1024 * 1024,
            num_threads=1,
        ),
        ProcessInfo(
            pid=2450,
            create_time=1700000120.5,
            ppid=1820,
            name="python3",
            username="student",
            status="R",
            cpu_percent=14.5,
            rss_bytes=48 * 1024 * 1024,
            num_threads=4,
        ),
        ProcessInfo(
            pid=3102,
            create_time=1700000300.2,
            ppid=2450,
            name="demo_worker",
            username="student",
            status="T",
            cpu_percent=None,
            rss_bytes=8 * 1024 * 1024,
            num_threads=1,
        ),
    ]