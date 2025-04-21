from flask import Blueprint

from router.apple_music.now_playing import now_playing_app

apple_music_app = Blueprint("apple_music", __name__, url_prefix="/apple-music")

apple_music_app.register_blueprint(now_playing_app)
