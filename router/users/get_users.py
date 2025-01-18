from flask import Blueprint, jsonify, request

from model.users import RoleType, User
from util.encryptor import encrypt
from util.request import handle_error, handle_access_token

get_user_app = Blueprint("get_users_app", __name__)

@get_user_app.route("/get-users", methods=["GET"])
@handle_access_token
@handle_error
def get_users():
    user = request.user
    query = request.args

    if user.role != RoleType.ADMIN:
        raise Exception("users do not have admin role")

    limit = int(query.get("limit", 20))
    offset = int(query.get("offset", 0))

    if query.get("text", False):
        text = encrypt(query.get("text", ""))
        all_user = User().filter(filters=[("id", ">=", offset), "and",
                                          ("username", "=", text), "or",
                                          ("email", "=", text)], limit=limit + 1)
    else:
        all_user = User().filter(filters=[("id", ">=", offset)], limit=limit + 1)

    response = []

    for user in all_user[:limit]:
        response.append({
            "uid": user.id,
            "username": user.username,
            "email": user.email,
            "role": str(user.role.name),
            "image_url": user.image_url
        })

    return jsonify({
        "datas": response,
        "next": -1 if len(response) < limit else all_user[-1].id,
    })
