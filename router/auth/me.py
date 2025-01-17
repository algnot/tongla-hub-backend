from flask import Blueprint, jsonify, request
from util.request import handle_error, handle_access_token

me_app = Blueprint("me", __name__)

@me_app.route("/me", methods=["GET"])
@handle_access_token
@handle_error
def me():
    user = request.user

    return jsonify({
        "uid": user.id,
        "email": user.email,
        "username": user.username,
        "image_url": user.image_url or "",
        "role": str(user.role.name),
    })
