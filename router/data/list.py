from flask import Blueprint, jsonify, request

from model.users import RoleType, User
from model.email import Email
from model.one_time_password import OneTimePassword
from util.encryptor import encrypt
from util.request import handle_error, handle_access_token

list_data_app = Blueprint("list_data_app", __name__)

mapper = {
    "user": {
        "model": User,
        "offset": "id",
        "filter": ["username", "email"],
        "filter_operator": "=",
        "role": RoleType.ADMIN,
        "mapper_key": ["uid", "username", "email", "role", "image_url"],
        "mapper_value": ["id", "username", "email", "role.name", "image_url"],
        "need_encrypt": True,
    },
    "email": {
        "model": Email,
        "offset": "id",
        "filter": ["to_email"],
        "filter_operator": "=",
        "role": RoleType.ADMIN,
        "mapper_key": ["id", "to_email", "template_id", "status", "reason", "send_at"],
        "mapper_value": ["id", "to_email", "template_id", "status", "reason", "send_at"],
        "need_encrypt": True,
    },
    "otp": {
        "model": OneTimePassword,
        "offset": "id",
        "filter": ["ref"],
        "filter_operator": "ilike",
        "role": RoleType.ADMIN,
        "mapper_key": ["id", "ref", "code", "used", "expires_at"],
        "mapper_value": ["id", "ref", "code", "used", "expires_at"],
        "need_encrypt": False,
    }
}

def resolve_nested_attribute(obj, attr_path):
    attrs = attr_path.split(".")
    for attr in attrs:
        obj = getattr(obj, attr, None)
        if obj is None:
            break
    return obj

@list_data_app.route("/list", methods=["GET"])
@handle_access_token
@handle_error
def list_data():
    user = request.user
    query = request.args
    model = query.get("model", "")
    limit = int(query.get("limit", 20))
    offset = query.get("offset", False)
    search_key = query.get("text", False)

    if model not in mapper.keys():
        raise Exception("model is not in mapper")

    if user.role != mapper[model]["role"]:
        raise Exception("users do not have admin role")

    filter_list = []
    if offset:
        filter_list.append((mapper[model]["offset"], "<=", int(offset)))

    if search_key:
        if offset:
            filter_list.append("and")
        if mapper[model]["need_encrypt"]:
            search_key = encrypt(search_key)

        filter_list = []
        filters_base = mapper[model]["filter"]
        for index, value in enumerate(filters_base):
            condition = (value, mapper[model]["filter_operator"], search_key)
            filter_list.append(condition)

            if index < len(filters_base) - 1:
                filter_list.append("or")

    datas = mapper[model]["model"]().filter(filters=filter_list, limit=limit + 1, order_by=[(mapper[model]["offset"], "desc")])
    response = []

    for data in datas[:limit]:
        to_append = {}
        for index, key in enumerate(mapper[model]["mapper_key"]):
            attr_path = mapper[model]["mapper_value"][index]
            to_append[key] = resolve_nested_attribute(data, attr_path)
        response.append(to_append)

    return jsonify({
        "datas": response,
        "next": -1 if len(response) < limit else getattr(datas[-1], mapper[model]["offset"]),
    })
