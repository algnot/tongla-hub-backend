from flask import Blueprint, jsonify, request

from model.question import Question
from model.test_case import TestCase
from model.users import User
from model.users import RoleType
from util.request import handle_error, handle_access_token, validate_request

update_quest_app = Blueprint("update_quest_app", __name__)

@update_quest_app.route("/update-question", methods=["PUT"])
@handle_access_token
@validate_request(["id", "title", "description", "start_code", "test_cases"])
@handle_error
def add_question():
    user = request.user
    payload = request.get_json()
    keys = payload.keys()

    if not isinstance(payload.get("test_cases"), list):
        raise ValueError("test_cases is not a list")

    exiting_question = Question().filter([("id", "=", payload["id"])], limit=1)

    if len(exiting_question) == 0:
        raise ValueError("No question found")

    exiting_question = exiting_question[0]
    if user.role != RoleType.ADMIN and exiting_question.owner_id != user.id:
        raise ValueError("User does not have permission to update this question")

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

    exiting_question.update(values)
    owner = User().filter([("id", "=", user.id)], limit=1)[0]

    old_test_cases = TestCase().filter([("question_id", "=", exiting_question.id)])
    for test_case in old_test_cases:
        test_case.unlink()

    new_test_case_response = []
    for test_case in payload["test_cases"]:
        created_test_case = TestCase().create({
            "input": test_case.get("input", ""),
            "expected": test_case.get("expected", ""),
            "expected_run_time_ms": test_case.get("expected_run_time_ms", 100),
            "question_id": exiting_question.id,
        })
        new_test_case_response.append({
            "id": created_test_case.id,
            "expected": created_test_case.expected,
            "expected_run_time_ms": created_test_case.expected_run_time_ms,
        })

    return jsonify({
        "id": exiting_question.id,
        "title": exiting_question.title,
        "description": exiting_question.description,
        "start_code": exiting_question.start_code,
        "rate": exiting_question.rate,
        "owner": {
            "username": owner.username,
        },
        "is_system_question": exiting_question.is_system_question,
        "is_public": exiting_question.is_public,
        "submitted": exiting_question.submitted,
        "commented": exiting_question.commented,
        "created_at": exiting_question.created_at,
        "test_cases": new_test_case_response,
    })
