from flask import Blueprint, jsonify, request
from util.request import handle_error, handle_refresh_token
from model.user_tokens import UserTokens

token_app = Blueprint("token", __name__)

@token_app.route("/generate-access-token", methods=["GET"])
@handle_refresh_token
@handle_error
def me():
    user = request.user

    user_token = UserTokens()
    user_token.user_id = user.id
    access_token = user_token.generate_access_token()

    return jsonify({
        "access_token": access_token
    })
