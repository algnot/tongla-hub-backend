import asyncio
import logging
import threading
from flask import Flask, jsonify
from flask_cors import CORS
from consumer.init_consumer import init_consumer
from cron.init_cron import init_cron
from router.apple_music.apple_music import apple_music_app
from router.apple_music.now_playing import connect_websocket
from router.auth.auth import auth_app
from router.code.code import code_app
from router.data.data import data_app
from router.uploader.uploader import uploader_app
from router.user.user import user_app
from web_socket.init_socket import init_web_socket_server
from util.config import get_config

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_app)
app.register_blueprint(data_app)
app.register_blueprint(code_app)
app.register_blueprint(user_app)
app.register_blueprint(uploader_app)
app.register_blueprint(apple_music_app)


@app.route("/_hc", methods=["GET"])
def _hc():
    return jsonify({"status": "server is running"})

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    server_mode = get_config("SERVICE_NAME", "tongla-hub-server")
    logger.info(f"Starting {server_mode}")
    if server_mode == "tongla-hub-server":
        threading.Thread(target=lambda: asyncio.run(connect_websocket())).start()
        app.run(threaded=True,
                host=get_config("FLASK_RUN_HOST", "0.0.0.0"),
                port=int(get_config("FLASK_RUN_PORT", 9000)),
                debug=get_config("FLASK_RUN_DEBUG", "true") == "true")
    elif server_mode == "tongla-hub-consumer":
        init_consumer()
    elif server_mode == "tongla-hub-socket-server":
        asyncio.run(init_web_socket_server())
    elif server_mode == "tongla-hub-cron":
        init_cron()
    else:
        raise RuntimeError("unknown server mode")
