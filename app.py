from flask import Flask, jsonify
from flask_cors import CORS

from router.auth.auth import auth_app
from router.users.users import users_app

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_app)
app.register_blueprint(users_app)

@app.route("/_hc", methods=["GET"])
def _hc():
    return jsonify({"status": "server is running"})

if __name__ == "__main__":
    app.run()
