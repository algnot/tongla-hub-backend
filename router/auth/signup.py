from flask import Blueprint, jsonify, request
from werkzeug.routing import ValidationError

from util.encryptor import encrypt, verify_password
from util.request import validate_request, handle_error
from model.users import User


sign_in_app = Blueprint("sign_in", __name__)

@sign_in_app.route("/sign-up", methods=["POST"])
@validate_request(["username", "email", "password"])
@handle_error
def sign_up():
    payload = request.get_json()

    user = User()
    user.username = payload["username"]
    user.email = payload["email"]
    user_created = user.sign_up(payload["password"])
    refresh_token, access_token = user_created.generate_token()

    return jsonify({
        "user_id": user_created.id,
        "email": user_created.email,
        "username": user_created.username,
        "role": str(user_created.role.name),
        "image_url": user_created.image_url or "",
        "refresh_token": refresh_token,
        "access_token": access_token,
    })

@sign_in_app.route("/login", methods=["POST"])
@validate_request(["email", "password"])
@handle_error
def login():
    payload = request.get_json()

    encrypted_email = encrypt(payload["email"])
    user = User().filter([("email", "=", encrypted_email)])

    if not user:
        raise ValidationError(f"user with email {payload['email']} not found")

    user = user[0]
    if not verify_password(payload["password"], user.hashed_password):
        raise ValidationError("user with email and password incorrect")

    refresh_token, access_token = user.generate_token()

    return jsonify({
        "user_id": user.id,
        "email": user.email,
        "username": user.username,
        "role": str(user.role.name),
        "image_url": user.image_url or "",
        "refresh_token": refresh_token,
        "access_token": access_token,
    })
