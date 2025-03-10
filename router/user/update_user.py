from flask import Blueprint, jsonify, request

from model.users import RoleType, User
from util.request import handle_error, handle_access_token, validate_request

update_user_app = Blueprint("update_user", __name__)

@update_user_app.route("/<string:user_id>", methods=["PUT"])
@handle_access_token
@handle_error
def get_user_by_id(user_id):
    user = request.user
    payload = request.get_json()

    if user.role != RoleType.ADMIN and user.id != int(user_id):
        raise Exception("Access denied")

    if payload.get("role", False) != RoleType.USER.name and user.role != RoleType.ADMIN:
        raise Exception("User can not update role of user")

    exiting_user = User().filter(filters=[("id", "=", user_id)], limit=1)

    if not exiting_user:
        raise Exception(f"No user found with id {user_id}")

    updated_user = exiting_user[0].update({
        "username": payload.get("username", exiting_user[0].username),
        "email": payload.get("email", exiting_user[0].email),
        "role": payload.get("role", exiting_user[0].role),
        "image_url": payload.get("image_url", exiting_user[0].image_url),
    })

    return jsonify({
        "uid": updated_user.id,
        "username": updated_user.username,
        "email": updated_user.email,
        "role": str(updated_user.role),
        "image_url": updated_user.image_url,
        "created_at": updated_user.created_at,
        "updated_at": updated_user.updated_at,
    })
