from flask import Blueprint, jsonify, request
from util.code import execute_code
from util.request import handle_error, validate_request


execute_app = Blueprint("execute_app", __name__)

@execute_app.route("/execute", methods=["POST"])
@validate_request(["stdin", "code"])
@handle_error
def execute():
    payload = request.get_json()
    code = payload.get("code")
    stdin = payload.get("stdin", "")

    response = execute_code(stdin, code)

    return jsonify(response)
