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
    mode = query.get("mode", "all")
    rate = query.get("rate", "all")

    if offset:
        if int(offset) > 0:
            filter_list = [("id", ">=", int(offset))]
        else:
            filter_list = []
    else:
        filter_list = []

    if mode in ["submitted", "not_submitted"]:
        all_submit = Submit().filter(filters=[("owner_id", "=", user.id)])
        all_submit_question_ids = [submit.question_id for submit in all_submit]
        if mode == "submitted":
            filter_list.append(("id", "in", all_submit_question_ids))
        else:
            filter_list.append(("id", "not in", all_submit_question_ids))

    if rate != "all":
        filter_list.append(("rate", "=", int(rate)))

    filter_list.append(("is_public", "=", True))

    questions = Question().filter(filters=filter_list, order_by=[("id", "asc")],
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