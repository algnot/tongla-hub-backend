import subprocess
import time
import os
import ast
from flask import Blueprint, jsonify, request
from util.request import handle_error, validate_request


execute_app = Blueprint("execute_app", __name__)

TIMEOUT_SECONDS = 20
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
                        raise PermissionError(f"usage of '{alias.name}' is not allowed.")
    except SyntaxError:
        pass

    os.environ["PATH"] = "/usr/bin:/bin"

@execute_app.route("/execute", methods=["POST"])
@validate_request(["stdin", "code"])
@handle_error
def execute():
    payload = request.get_json()
    code = payload.get("code")
    stdin = payload.get("stdin", "")

    start_time = time.time()

    try:
        restrict_execution(code)

        process = subprocess.Popen(
            ['python3', '-c', code],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        stdout, stderr = process.communicate(input=stdin, timeout=TIMEOUT_SECONDS)
        runtime = time.time() - start_time

        return jsonify({
            "stdout": stdout,
            "stderr": stderr,
            "runtime": int(runtime * 1000),
            "runtime_unit": "ms"
        })
    except subprocess.TimeoutExpired:
        process.kill()
        runtime = time.time() - start_time
        return jsonify({
            "stdout": "",
            "stderr": f"Timeout Error: process timed out after {TIMEOUT_SECONDS} seconds.",
            "runtime": int(runtime * 1000),
            "runtime_unit": "ms"
        })
    except PermissionError as e:
        return jsonify({
            "stdout": "",
            "stderr": f"Permission error: {str(e)}. Are you hacker?",
            "runtime": 0,
            "runtime_unit": "ms"
        })
