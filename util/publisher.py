import json
import pika
from util.config import get_config


class Publisher:

    def __init__(self):
        self.host = get_config("RABBITMQ_HOST", "localhost")
        self.port = get_config("RABBITMQ_PORT", "5672")
        self.username = get_config("RABBITMQ_DEFAULT_USER", "root")
        self.password = get_config("RABBITMQ_DEFAULT_PASS", "root")

    def create_connection(self):
        credentials = pika.PlainCredentials(self.username, self.password)
        param = pika.ConnectionParameters(host=self.host, port=self.port, credentials=credentials)
        return pika.BlockingConnection(param)

    def publish(self, exchange, routing_key, message):
        connection = self.create_connection()
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange, exchange_type="topic")
        channel.basic_publish(exchange=exchange, routing_key=routing_key, body= json.dumps(message))
