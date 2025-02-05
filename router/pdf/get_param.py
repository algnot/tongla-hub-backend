from flask import Blueprint, jsonify, request
from util.request import handle_error
import pypdftk
import requests
import tempfile
import os

get_pdf_params_app = Blueprint("get_pdf_params", __name__)

@get_pdf_params_app.route("/get-params", methods=["POST"])
@handle_error
def get_pdf_params():
    url = request.json["url"]

    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"error": "Failed to download PDF"}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(response.content)
        temp_pdf_path = temp_pdf.name

    try:
        raw_fields = pypdftk.dump_data_fields(temp_pdf_path)
    finally:
        os.remove(temp_pdf_path)

    return jsonify(raw_fields)