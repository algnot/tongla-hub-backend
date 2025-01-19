from flask import Flask, jsonify
from flask_cors import CORS

from router.auth.auth import auth_app
from router.code.code import code_app
from router.data.data import data_app

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_app)
app.register_blueprint(data_app)

app.register_blueprint(code_app)

@app.route("/_hc", methods=["GET"])
def _hc():
    return jsonify({"status": "server is running"})

if __name__ == "__main__":
    app.run()
