import os
# Direct communication bridge to the Linux Kernel through the /proc virtual filesystem.
# Responsible for raw data retrieval, parsing, and data normalization.

def read_proc_status(pid: int) -> dict[str, str | int] | None:
    status_path = f"/proc/{pid}/status"
    raw_fields: dict[str, str] = {}

    try:
        with open(status_path, "r", encoding="utf-8") as f:
            for line in f:
                if ":" not in line:
                    continue
                key, value = line.split(":", 1)
                raw_fields[key.strip()] = value.strip()
    except (FileNotFoundError, ProcessLookupError, PermissionError, OSError):
        return None
# Data extraction and normalization
    try:
        name = raw_fields.get("Name", "unknown")
        state_raw = raw_fields.get("State", "?")
        status = state_raw.split()[0] if state_raw else "?"
        parsed_pid = int(raw_fields.get("Pid", pid))
        ppid = int(raw_fields.get("PPid", 0))
        num_threads = int(raw_fields.get("Threads", 1))

        rss_bytes = 0
        if "VmRSS" in raw_fields:
            rss_parts = raw_fields["VmRSS"].split()
            if rss_parts and rss_parts[0].isdigit():
                rss_bytes = int(rss_parts[0]) * 1024

        return {
            "pid": parsed_pid,
            "ppid": ppid,
            "name": name,
            "status": status,
            "rss_bytes": rss_bytes,
            "num_threads": num_threads,
        }
    except (ValueError, IndexError):
        return None

# Validation and comparison function
def verify_against_proc(pid: int) -> dict[str, str | int] | None:
    if not os.path.exists(f"/proc/{pid}"):
        return None
    return read_proc_status(pid)