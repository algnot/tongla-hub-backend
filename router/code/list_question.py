from flask import Blueprint, jsonify, request

from model.question import Question
from model.submit import Submit
from util.request import handle_error, handle_access_token


list_question_app = Blueprint("list_question_app", __name__)

@list_question_app.route("/list-question", methods=["GET"])
@handle_access_token
@handle_error
def get_question():
    user = request.user
    query = request.args
    limit = int(query.get("limit", 20))
    offset = query.get("offset", False)

    if offset:
        if int(offset) > 0:
            offset_filter = [("id", "<=", int(offset))]
        else:
            offset_filter = []
    else:
        offset_filter = []

    questions = Question().filter(filters=offset_filter, order_by=[("id", "desc")],
                                  limit=limit + 1)
    response = []

    for question in questions[:limit]:
        question_id = question.id
        submit = Submit().filter(filters=[("question_id", "=", question_id),
                                          ("owner_id", "=", user.id)])

        is_submit = False
        is_passed = False
        if len(submit) > 0:
            is_submit = True
            is_passed = submit[0].max_score == submit[0].score

        response.append({
            "id": question_id,
            "title": question.title,
            "rate": question.rate,
            "submitted": question.submitted,
            "is_submit": is_submit,
            "is_passed": is_passed,
            "created_at": question.created_at,
            "updated_at": question.updated_at,
        })

    return jsonify({
        "datas": response,
        "next": -1 if len(response) < limit else getattr(questions[-1], "id"),
    })