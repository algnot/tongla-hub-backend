from flask import Blueprint, jsonify, request

from model.question import Question
from model.submit import Submit, SubmitState
from util.publisher import Publisher
from util.request import validate_request, handle_error, handle_access_token

submit_code_app = Blueprint("submit_code_app", __name__)

@submit_code_app.route("/submit", methods=["POST"])
@validate_request(["question_id", "code"])
@handle_access_token
@handle_error
def submit_code():
    user = request.user
    payload = request.get_json()
    code = payload.get("code")
    question_id = payload.get("question_id", "")

    exiting_question = Question().filter([("id", "=", question_id)], limit=1)

    if len(exiting_question) == 0:
        raise ValueError("not found question")

    exiting_question = exiting_question[0]

    submit = Submit().filter(filters=[("question_id", "=", exiting_question.id), ("owner_id", "=", user.id)], limit=1)

    if len(submit) == 0:
        submit = Submit().create({
            "question_id": exiting_question.id,
            "owner_id": user.id,
            "code": code,
            "status": SubmitState.PENDING,
        })
        exiting_question.update({
            "submitted": exiting_question.submitted + 1
        })
    else:
        submit = submit[0].update({
            "question_id": exiting_question.id,
            "owner_id": user.id,
            "code": code,
            "status": SubmitState.PENDING,
        })

    Publisher().publish(exchange="question", routing_key="submit", message={
        "submit_id": submit.id,
        "question_id": exiting_question.id,
        "owner_id": user.id,
        "code": code,
    })

    return jsonify({
        "id": submit.id,
        "status": str(submit.status.name)
    })
