from flask import Blueprint

from router.auth.me import me_app
from router.auth.signup import sign_in_app
from router.auth.token import token_app

auth_app = Blueprint("auth", __name__, url_prefix="/auth")

auth_app.register_blueprint(sign_in_app)
auth_app.register_blueprint(me_app)
auth_app.register_blueprint(token_app)
