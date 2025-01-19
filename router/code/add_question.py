from flask import Blueprint, jsonify, request

from model.question import Question
from model.test_case import TestCase
from model.users import RoleType
from util.request import handle_error, handle_access_token, validate_request

add_quest_app = Blueprint("add_quest_app", __name__)

@add_quest_app.route("/add-question", methods=["POST"])
@handle_access_token
@validate_request(["title", "description", "start_code", "test_cases"])
@handle_error
def add_question():
    user = request.user
    payload = request.get_json()
    keys = payload.keys()

    if not isinstance(payload.get("test_cases"), list):
        raise ValueError("test_cases is not a list")

    values = {
        "title": payload["title"],
        "description": payload["description"],
        "start_code": payload["start_code"],
        "owner_id": user.id,
        "rate": payload.get("rate", 1),
    }

    if user.role == RoleType.ADMIN:
        if "is_system_question" in keys:
            values["is_system_question"] = payload["is_system_question"]
        if "is_public" in keys:
            values["is_public"] = payload["is_public"]

    question = Question().create(values)

    test_case_response = []
    for test_case in payload["test_cases"]:
        created_test_case = TestCase().create({
            "input": test_case.get("input", ""),
            "expected": test_case.get("expected", ""),
            "expected_run_time_ms": test_case.get("expected_run_time_ms", 100),
            "question_id": question.id,
        })
        test_case_response.append({
            "id": created_test_case.id,
            "expected": created_test_case.expected,
            "expected_run_time_ms": created_test_case.expected_run_time_ms,
        })

    return jsonify({
        "id": question.id,
        "title": question.title,
        "description": question.description,
        "start_code": question.start_code,
        "rate": question.rate,
        "owner": {
            "username": user.username,
        },
        "is_system_question": question.is_system_question,
        "is_public": question.is_public,
        "submitted": question.submitted,
        "commented": question.commented,
        "created_at": question.created_at,
        "test_cases": test_case_response,
    })
