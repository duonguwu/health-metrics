import pika
import json
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")

def get_connection():
    """Thiết lập kết nối với RabbitMQ"""
    return pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=pika.PlainCredentials("admin", "admin")))

def publish_message(queue_name, message):
    """Gửi message vào queue cụ thể"""
    connection = get_connection()
    channel = connection.channel()

    # Đảm bảo queue tồn tại
    channel.queue_declare(queue=queue_name, durable=True)

    # Chuyển đổi message sang JSON
    message_body = json.dumps(message)

    # Gửi message với độ bền
    channel.basic_publish(
        exchange="",
        routing_key=queue_name,
        body=message_body,
        properties=pika.BasicProperties(
            delivery_mode=2,  # Persistent messages
        )
    )

    connection.close()
