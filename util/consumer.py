import json
import pika
from util.config import get_config


class Consumer:

    def __init__(self, exchange, queue_name, routing_key, callback):
        self.host = get_config("RABBITMQ_HOST", "localhost")
        self.port = get_config("RABBITMQ_POST", "5672")
        self.username = get_config("RABBITMQ_DEFAULT_USER", "root")
        self.password = get_config("RABBITMQ_DEFAULT_PASS", "root")
        self.exchange = exchange
        self.queue_name = queue_name
        self.routing_key = routing_key
        self.connection = self.create_connection()
        self.callback = callback

    def __del__(self):
        self.connection.close()

    def create_connection(self):
        credentials = pika.PlainCredentials(self.username, self.password)
        param = pika.ConnectionParameters(host=self.host, port=self.port, credentials=credentials)
        return pika.BlockingConnection(param)

    def on_message_callback(self, channel, method, properties, body):
        routing_key = method.routing_key
        print(f"received new message for exchange={self.exchange} queue_name={self.queue_name} routing_key={routing_key} body={body}")
        self.callback(json.loads(body))

    def setup(self):
        channel = self.connection.channel()
        channel.exchange_declare(exchange=self.exchange, exchange_type="topic")
        channel.queue_declare(queue=self.queue_name)
        channel.queue_bind(queue=self.queue_name, exchange=self.exchange, routing_key=self.routing_key)
        channel.basic_consume(queue=self.queue_name, on_message_callback=self.on_message_callback, auto_ack=True)
        try:
            print(f"start consuming exchange exchange={self.exchange} queue_name={self.queue_name} routing_key={self.routing_key}")
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()