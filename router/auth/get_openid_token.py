import requests
import random
import string
from flask import Blueprint, request, jsonify
from model.users import User
from util.config import get_config
from util.encryptor import encrypt, hash_password
from util.request import handle_error, validate_request

get_openid_token_app = Blueprint("get_openid_token", __name__)

@get_openid_token_app.route("/get-openid-token", methods=["POST"])
@validate_request(["code"])
@handle_error
def get_openid_token():
    payload = request.get_json()

    client_id = get_config("OPENID_CLIENT_ID", "")
    client_secret = get_config("OPENID_CLIENT_SECRET", "")
    token_endpoint = get_config("OPENID_TOKEN_ENDPOINT", "")
    user_info_endpoint = get_config("OPENID_USERINFO_ENDPOINT", "")
    redirect_uri = get_config("OPENID_CLIENT_REDIRECT_URI", "")
    token_endpoint = f"{token_endpoint}?grant_type=authorization_code&client_id={client_id}&client_secret={client_secret}&redirect_uri={redirect_uri}&code={payload['code']}"

    response = requests.request("POST", token_endpoint)
    if response.status_code != 200:
        raise Exception(response.text)

    id_token = response.json()["id_token"]

    user_info = requests.request("GET", user_info_endpoint, headers={
        "Accept": "application/json",
        "Authorization": f"Bearer {id_token}"
    })
    if user_info.status_code != 200:
        raise Exception(user_info.text)

    email = user_info.json()["email"]
    user = User().filter(filters=[("email", "=", encrypt(email))])

    if len(user) == 0:
        random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        user = User().create({
            "username": user_info.json()["username"],
            "email": email,
            "hashed_password": hash_password(random_password)
        })
    else:
        user = user[0]

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
