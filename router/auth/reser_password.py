from flask import Blueprint, jsonify, request
from werkzeug.routing import ValidationError

from model.email import Email
from model.one_time_password import OneTimePassword
from model.user_tokens import UserTokens, TokenType
from util.config import get_config
from util.encryptor import encrypt
from util.request import handle_error, validate_request, handle_token
from model.users import User

reset_password_otp_app = Blueprint("reset_password_otp_app", __name__)

@reset_password_otp_app.route("/reset-password-otp", methods=["POST"])
@validate_request(["email"])
@handle_error
def reset_password_otp():
    payload = request.get_json()
    find_user = User().filter(filters=[("email", "=", encrypt(payload["email"]))])

    if len(find_user) < 1:
        raise ValidationError("No user found")

    otp = OneTimePassword().create({
        "mapper_key": "RESET_PASSWORD",
        "mapper_value": find_user[0].id
    })

    Email().create({
        "to_email": payload["email"],
        "template_id": get_config("EMAIL_API_TEMPLATE_ID"),
    }).send_email({
        "to_name": find_user[0].username,
        "otp": otp.code,
        "to_email": payload["email"],
        "ref": otp.ref
    })

    return jsonify({
        "ref": otp.ref,
        "email": payload["email"],
        "mapper_key": otp.mapper_key,
        "mapper_value": otp.mapper_value,
        "expires_at": otp.expires_at,
    })

@reset_password_otp_app.route("/reset-password-token", methods=["POST"])
@validate_request(["code", "ref", "email"])
@handle_error
def reset_password_token():
    payload = request.get_json()
    find_user = User().filter(filters=[("email", "=", encrypt(payload["email"]))])

    if len(find_user) < 1:
        raise ValidationError("No user found")

    otp = OneTimePassword().filter([("ref", "=", payload["ref"]),
                                    ("used", "=", False),
                                    ("mapper_value", "=", find_user[0].id),
                                    ("mapper_key", "=", "RESET_PASSWORD")])

    if len(otp) == 0:
        raise ValidationError("No otp with ref found")

    if otp[0].code != payload["code"]:
        raise ValidationError(f"Wrong code ref ({otp[0].ref})")

    token = UserTokens().generate_reset_password_token(user_id=find_user[0].id)
    otp[0].update({
        "used": True
    })

    return jsonify({
        "token": token
    })

@reset_password_otp_app.route("/reset-password", methods=["POST"])
@validate_request(["password"])
@handle_token
@handle_error
def reset_password():
    user = request.user
    token = request.token

    if token.get("type") != str(TokenType.RESET_PASSWORD.value):
        raise ValidationError("Wrong token type")

    refresh_token, access_token  = user.change_password(request.get_json()["password"]).generate_token()
    UserTokens().filter(filters=[("id", "=", token.get("sub", {}).get("token_id"))], limit=1)[0].update({
        "revoked": True
    })

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    })
