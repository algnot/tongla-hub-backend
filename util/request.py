from functools import wraps
from flask import request, jsonify
from model.user_tokens import UserTokens, TokenType
from model.users import User


def validate_request(required_fields):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            payload = request.get_json()

            missing_fields = []
            for field in required_fields:
                if field not in payload or payload[field] is None:
                    missing_fields.append(field)

            if missing_fields:
                return jsonify({
                    "status": False,
                    "message": f"Missing fields: {', '.join(missing_fields)}"
                }), 400
            return func(*args, **kwargs)
        return wrapper
    return decorator

def handle_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_message = str(e)

            return jsonify({
                "status": False,
                "message": error_message
            }), 400
    return wrapper

def get_user_from_token(token: str, token_type=TokenType.ACCESS):
    payload = UserTokens().verify_token(token)

    if payload["type"] != str(token_type.value):
        raise ValueError("Invalid token")

    return payload

def handle_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"status": False, "message": "Authorization token missing"}), 403

        token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None
        if not token:
            return jsonify({"status": False, "message": "Invalid token format"}), 403

        try:
            payload = UserTokens().verify_token(token)
            user = User().get_by_id(payload["sub"]["user_id"])
            request.user = user
            request.token = payload
        except Exception as e:
            return jsonify({"status": False, "message": str(e)}), 403

        return func(*args, **kwargs)

    return wrapper

def handle_access_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"status": False, "message": "Authorization token missing"}), 403

        token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None
        if not token:
            return jsonify({"status": False, "message": "Invalid token format"}), 403

        try:
            user_id = get_user_from_token(token, TokenType.ACCESS)["sub"]["user_id"]
            user = User().get_by_id(user_id)
            request.user = user
        except Exception as e:
            return jsonify({"status": False, "message": str(e)}), 403

        return func(*args, **kwargs)

    return wrapper

def handle_refresh_token(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({"status": False, "message": "Authorization token missing"}), 403

        token = auth_header.split(" ")[1] if len(auth_header.split(" ")) > 1 else None
        if not token:
            return jsonify({"status": False, "message": "Invalid token format"}), 403

        try:
            user_id = get_user_from_token(token, TokenType.REFRESH)["sub"]["user_id"]
            user = User().get_by_id(user_id)
            request.user = user
        except Exception as e:
            return jsonify({"status": False, "message": str(e)}), 403

        return func(*args, **kwargs)

    return wrapper

