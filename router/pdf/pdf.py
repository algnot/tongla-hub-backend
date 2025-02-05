from flask import Blueprint

from router.pdf.fill_pdf import fill_pdf_app
from router.pdf.get_param import get_pdf_params_app

pdf_app = Blueprint("pdf", __name__, url_prefix="/pdf")

pdf_app.register_blueprint(get_pdf_params_app)
pdf_app.register_blueprint(fill_pdf_app)
