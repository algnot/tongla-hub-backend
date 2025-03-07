from flask import Blueprint

from router.code.add_question import add_quest_app
from router.code.execute import execute_app
from router.code.get_question import get_question_app
from router.code.list_question import list_question_app
from router.code.submit import submit_code_app
from router.code.update_question import update_quest_app

code_app = Blueprint("code_app", __name__, url_prefix="/code")

code_app.register_blueprint(execute_app)
code_app.register_blueprint(add_quest_app)
code_app.register_blueprint(update_quest_app)
code_app.register_blueprint(get_question_app)
code_app.register_blueprint(submit_code_app)
code_app.register_blueprint(list_question_app)
