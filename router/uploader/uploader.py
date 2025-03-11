from flask import Blueprint
from router.uploader.upload_file import upload_file_app


uploader_app = Blueprint("uploader", __name__, url_prefix="/uploader")
uploader_app.register_blueprint(upload_file_app)