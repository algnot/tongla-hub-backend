from flask import Blueprint

from router.auth.get_openid_token import get_openid_token_app
from router.auth.me import me_app
from router.auth.reser_password import reset_password_otp_app
from router.auth.signup import sign_in_app
from router.auth.token import token_app

auth_app = Blueprint("auth", __name__, url_prefix="/auth")

auth_app.register_blueprint(sign_in_app)
auth_app.register_blueprint(me_app)
auth_app.register_blueprint(token_app)
auth_app.register_blueprint(reset_password_otp_app)
auth_app.register_blueprint(get_openid_token_app)
