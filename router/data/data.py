from flask import Blueprint

from router.data.list import list_data_app

data_app = Blueprint("data", __name__, url_prefix="/data")

data_app.register_blueprint(list_data_app)
