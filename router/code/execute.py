import subprocess
import time
import os
from flask import Blueprint, jsonify, request
from util.request import handle_error, validate_request

execute_app = Blueprint("execute_app", __name__)

TIMEOUT_SECONDS = 20

def restrict_execution():
    os.setuid(1000)
    os.setgid(1000)

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
        restrict_execution()

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
            "stderr": f"Error: Process timed out after {TIMEOUT_SECONDS} seconds.",
            "runtime": int(runtime * 1000),
            "runtime_unit": "ms"
        })
