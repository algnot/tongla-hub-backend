from flask import Blueprint, jsonify, request

from model.question import Question
from model.test_case import TestCase
from model.users import User
from util.request import handle_error

get_question_app = Blueprint("get_question_app", __name__)

@get_question_app.route("/get-question-by-id", methods=["GET"])
@handle_error
def get_question():
    question_id = request.args.get("id", False)

    if not question_id:
        raise ValueError("missing question id")

    exiting_question = Question().filter([("id", "=", question_id)], limit=1)

    if len(exiting_question) == 0:
        raise ValueError("not found question")

    exiting_question = exiting_question[0]
    owner = User().filter([("id", "=", exiting_question.owner_id)], limit=1)[0]

    test_case_response = []
    test_cases = TestCase().filter([("question_id", "=", exiting_question.id)])
    for test_case in test_cases:
        test_case_response.append({
            "id": test_case.id,
            "input": test_case.input,
            "expected": test_case.expected,
            "expected_run_time_ms": test_case.expected_run_time_ms,
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
        "test_cases": test_case_response,
    })
