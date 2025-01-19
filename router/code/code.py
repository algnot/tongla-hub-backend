from flask import Blueprint
from router.code.execute import execute_app

code_app = Blueprint("code_app", __name__, url_prefix="/code")

code_app.register_blueprint(execute_app)
