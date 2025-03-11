from flask import Blueprint, jsonify, request
from util.request import handle_error, validate_request
from util.uploader import S3Uploader

upload_file_app = Blueprint("upload_file", __name__)

@upload_file_app.route("/upload", methods=["POST"])
@validate_request(["content", "content_type"])
@handle_error
def upload_file():
    payload = request.get_json()
    url = S3Uploader().upload_base64("uploader", payload["content"], payload["content_type"])

    return jsonify({
        "url": url
    })