from flask import Blueprint, jsonify, request

from model.users import RoleType, User
from util.request import handle_error, handle_access_token

get_user_app = Blueprint("get_user", __name__)

@get_user_app.route("/<string:user_id>", methods=["GET"])
@handle_access_token
@handle_error
def get_user_by_id(user_id):
    user = request.user

    if user.role != RoleType.ADMIN and user.id != int(user_id):
        raise Exception("Access denied")

    exiting_user = User().filter(filters=[("id", "=", user_id)], limit=1)

    if not exiting_user:
        raise Exception(f"No user found with id {user_id}")

    return jsonify({
        "uid": exiting_user[0].id,
        "username": exiting_user[0].username,
        "email": exiting_user[0].email,
        "role": str(exiting_user[0].role.name),
        "image_url": exiting_user[0].image_url,
        "created_at": exiting_user[0].created_at,
        "updated_at": exiting_user[0].updated_at,
    })
