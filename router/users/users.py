from flask import Blueprint


from router.users.get_users import get_user_app

users_app = Blueprint("users", __name__, url_prefix="/users")

users_app.register_blueprint(get_user_app)
