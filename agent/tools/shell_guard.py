import shlex
import subprocess
import sys
from pathlib import Path


ALLOWED_PREFIXES = [
    ["npm", "install"],
    ["npm", "test"],
    ["npm", "run", "build"],
    ["npm", "run", "lint"],
    ["pnpm", "install"],
    ["pnpm", "test"],
    ["pnpm", "run", "build"],
    ["pnpm", "run", "lint"],
    ["yarn", "install"],
    ["yarn", "test"],
    ["yarn", "build"],
    ["pytest"],
    ["python", "-m", "pytest"],
]


def is_allowed_command(command: str) -> bool:
    try:
        parts = shlex.split(command)
    except ValueError:
        return False

    if not parts:
        return False

    for prefix in ALLOWED_PREFIXES:
        if parts[:len(prefix)] == prefix:
            return True

    return False


def run_allowed_command(command: str, cwd: Path) -> str:
    if not is_allowed_command(command):
        raise RuntimeError(f"Command is not allowed: {command}")

    print(f"[exec] Starting: {command}", flush=True)
    print(f"[exec] Working directory: {cwd}", flush=True)

    process = subprocess.Popen(
        shlex.split(command),
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    full_output = []
    if process.stdout:
        for line in process.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            full_output.append(line)

    process.wait()

    print(f"[exec] Finished with exit code {process.returncode}: {command}", flush=True)

    if process.returncode != 0:
        print(f"[exec] Command reported a non-zero exit code: {process.returncode}", flush=True)

    return "".join(full_output)
