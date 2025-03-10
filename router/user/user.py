from flask import Blueprint
from router.user.get_user import get_user_app
from router.user.update_user import update_user_app

user_app = Blueprint("user", __name__, url_prefix="/user")

user_app.register_blueprint(get_user_app)
user_app.register_blueprint(update_user_app)
