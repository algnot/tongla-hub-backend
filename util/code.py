import ast
import subprocess
import time
import os


TIMEOUT_SECONDS = 10
RESTRICTED_MODULES = ["os", "subprocess", "sys", "platform", "pathlib"]
ALLOWED_MODULES = [
    "time", "math", "random", "string", "itertools", "collections", "functools", "operator",
    "decimal", "fractions", "datetime", "json", "re", "uuid", "bisect", "heapq", "copy"
]

def restrict_execution(code):
    try:
        tree = ast.parse(code)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name not in ALLOWED_MODULES:
                        raise PermissionError(f"usage of '{alias.name}' is not allowed. allowed modules: {ALLOWED_MODULES}")
    except SyntaxError:
        pass

    os.environ["PATH"] = "/usr/bin:/bin"

def wrap_code(code):
    indented_code = "\n    ".join(code.splitlines())
    wrapped_code = f"""
try:
    {indented_code}
except EOFError:
    print("EOFError: Not enough input provided.", flush=True)
"""
    return wrapped_code

def execute_code(stdin, code):
    start_time = time.time()
    try:
        restrict_execution(code)
        wrapped_code = wrap_code(code)

        process = subprocess.Popen(
            ['python3', '-c', wrapped_code],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate(input=stdin, timeout=TIMEOUT_SECONDS)
        runtime = time.time() - start_time

        return {
            "stdout": stdout,
            "stderr": stderr,
            "runtime": int(runtime * 1000),
            "runtime_unit": "ms"
        }
    except subprocess.TimeoutExpired:
        process.kill()
        runtime = time.time() - start_time
        return {
            "stdout": "",
            "stderr": f"Timeout Error: process timed out after {TIMEOUT_SECONDS} seconds.",
            "runtime": int(runtime * 1000),
            "runtime_unit": "ms"
        }
    except PermissionError as e:
        return {
            "stdout": "",
            "stderr": f"Permission error: {str(e)} Are you hacker?",
            "runtime": 0,
            "runtime_unit": "ms"
        }
    except Exception:
        return {
            "stdout": "",
            "stderr": "EOFError: No input provided for execution.",
            "runtime": 0,
            "runtime_unit": "ms"
        }
