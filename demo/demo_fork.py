# Purpose: Create a child process using fork(), execute a worker using execvp(), and wait for it using waitpid().
# Run: python3 demo/demo_fork.py

import os
import sys


def main():
    worker_code = "import time; time.sleep(300)"

    pid = os.fork()

    if pid == 0:
        os.execvp(
            sys.executable,
            [sys.executable, "-c", worker_code]
        )

    print(f"CHILD_PID={pid}", flush=True)

    finished_pid, status = os.waitpid(pid, 0)

    if os.WIFEXITED(status):
        print(f"Child {finished_pid} exited with code {os.WEXITSTATUS(status)}")

    elif os.WIFSIGNALED(status):
        print(f"Child {finished_pid} terminated by signal {os.WTERMSIG(status)}")


if __name__ == "__main__":
    main()
