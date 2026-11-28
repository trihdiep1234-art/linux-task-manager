# Purpose: Safely terminate, suspend, and resume Linux processes using signals.
# Requirements: psutil
# Run: Imported by the GUI or other Python modules.

import os
import signal
import math
import psutil


def _get_process(pid, create_time):
    if not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0:
        raise ValueError("Invalid PID.")

    if (
        isinstance(create_time, bool)
        or not isinstance(create_time, (int, float))
        or not math.isfinite(create_time)
        or create_time <= 0
    ):
        raise ValueError("Invalid create_time.")

    if pid == os.getpid():
        raise PermissionError("Cannot control the application itself.")

    process = psutil.Process(pid)

    if process.create_time() != create_time:
        raise ProcessLookupError("Process identity mismatch.")

    return process


def _send_signal(pid, create_time, sig):
    try:
        process = _get_process(pid, create_time)
        process.send_signal(sig)

        return {
            "success": True,
            "message": f"Signal {sig} sent to PID {pid}."
        }

    except psutil.ZombieProcess:
        message = "Process is already a zombie."

    except psutil.NoSuchProcess:
        message = "Process does not exist."

    except psutil.AccessDenied:
        message = "Permission denied."

    except (ValueError, PermissionError, ProcessLookupError, OSError) as error:
        message = str(error)

    return {
        "success": False,
        "message": message
    }


def terminate(pid, create_time):
    return _send_signal(pid, create_time, signal.SIGTERM)


def suspend(pid, create_time):
    return _send_signal(pid, create_time, signal.SIGSTOP)


def resume(pid, create_time):
    return _send_signal(pid, create_time, signal.SIGCONT)
