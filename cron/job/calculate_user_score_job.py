from cron.init_cron import init_job
from model.question import Question
from model.submit import Submit
from model.users import User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@init_job("0 0 * * *")
def calculate_user_score_job():
    users = User().filter(filters=[])

    for user in users:
        all_submit = Submit().filter(filters=[("owner_id", "=", user.id)])
        score = 0

        for submit in all_submit:
            question = Question().get_by_id(submit.question_id)
            score += int((submit.score / submit.max_score) * 100) * question.rate

        logger.info(f"update score for {user.id}: {score} score")
        user.update({"score": score})
