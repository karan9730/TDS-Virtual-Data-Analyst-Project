# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

import subprocess
import tempfile
import os
import sys

# Directory where user code can read/write files
OUTPUT_DIR = "/tmp/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

MAX_TIMEOUT_SEC = 30  # hard max timeout enforced internally

def run_code_with_timeout(code: str, timeout_sec: int = 15) -> str:
    """
    Runs given Python code safely in a subprocess with a timeout.
    Returns stdout or error message.
    """
    # Cap timeout to MAX_TIMEOUT_SEC no matter what
    if timeout_sec > MAX_TIMEOUT_SEC:
        timeout_sec = MAX_TIMEOUT_SEC
    if timeout_sec <= 0:
        timeout_sec = 15  # default fallback timeout

    # If code contains escaped newlines, convert them to real newlines
    if "\\n" in code:
        code = code.encode().decode("unicode_escape")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", dir=OUTPUT_DIR, delete=False) as tmp_file:
        tmp_file.write(code)
        tmp_filename = tmp_file.name

    try:
        proc = subprocess.Popen(
            ["/usr/local/bin/python", "-I", tmp_filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=OUTPUT_DIR,
        )

        try:
            stdout, stderr = proc.communicate(timeout=timeout_sec)
        except subprocess.TimeoutExpired:
            proc.kill()
            return "[Error] Code execution timed out."

        if proc.returncode != 0:
            return f"[Error] Runtime error:\n{stderr.strip()}"

        return stdout.strip() or "[No output from code.]"

    finally:
        try:
            os.remove(tmp_filename)
        except Exception:
            pass

def execute_code(code: str, timeout_sec: int = 15) -> str:
    """
    Executes raw multi-line Python code safely.
    """
    forbidden = [
        "import os", "import sys", "import subprocess", "open(", "eval(", "exec(",
        "socket", "threading", "multiprocessing"
    ]
    if any(f in code for f in forbidden):
        return "[Error] Code contains forbidden operations."

    return run_code_with_timeout(code, timeout_sec)