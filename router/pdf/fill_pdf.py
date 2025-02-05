from flask import Blueprint, request, send_file, jsonify
from util.request import handle_error, validate_request
from util.request import handle_error
import pypdftk
import requests
import tempfile
import os

fill_pdf_app = Blueprint("fill_pdf", __name__)

@fill_pdf_app.route("/fill", methods=["POST"])
@validate_request(["url", "params"])
@handle_error
def fill_pdf():
    payload = request.get_json()
    url = payload["url"]
    fill_data = payload.get("params", {})

    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({"error": "Failed to download PDF"}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf.write(response.content)
        temp_pdf_path = temp_pdf.name

    output_pdf_path = f"{temp_pdf_path}_filled.pdf"

    try:
        pypdftk.fill_form(temp_pdf_path, fill_data, out_file=output_pdf_path, flatten=True)

        return send_file(output_pdf_path, as_attachment=True, download_name="filled_form.pdf", mimetype="application/pdf")

    finally:
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
        if os.path.exists(output_pdf_path):
            os.remove(output_pdf_path)
