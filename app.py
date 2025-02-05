import asyncio
from flask import Flask, jsonify
from flask_cors import CORS
from consumer.init_consumer import init_consumer
from router.auth.auth import auth_app
from router.code.code import code_app
from router.data.data import data_app
from router.pdf.pdf import pdf_app
from web_socket.init_socket import init_web_socket_server
from util.config import get_config

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_app)
app.register_blueprint(data_app)
app.register_blueprint(code_app)
app.register_blueprint(pdf_app)

@app.route("/_hc", methods=["GET"])
def _hc():
    return jsonify({"status": "server is running"})

if __name__ == "__main__":
    server_mode = get_config("SERVICE_NAME", "tongla-hub-server")
    if server_mode == "tongla-hub-server":
        app.run(threaded=True)
    elif server_mode == "tongla-hub-consumer":
        init_consumer()
    elif server_mode == "tongla-hub-socket-server":
        asyncio.run(init_web_socket_server())
    else:
        raise RuntimeError("unknown server mode")
