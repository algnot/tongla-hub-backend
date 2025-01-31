from consumer.submit_code import callback_submit
from util.consumer import Consumer


def init_consumer():
    Consumer(exchange="question", queue_name="question", routing_key="submit", callback=callback_submit).setup()
