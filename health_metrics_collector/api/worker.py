import pika
import json
import os

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")

def callback(ch, method, properties, body):
    """Hàm xử lý message từ RabbitMQ"""
    data = json.loads(body)
    print("Testing!!!")
    print(f"Received message: {data}")

    # Giả lập lưu trữ hoặc xử lý (ở đây chỉ in ra)
    # Bạn có thể lưu vào cơ sở dữ liệu khác hoặc kích hoạt cảnh báo
    ch.basic_ack(delivery_tag=method.delivery_tag)  # Xác nhận đã xử lý

def consume(queue_name):
    """Nhận message từ queue"""
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    # Đảm bảo queue tồn tại
    channel.queue_declare(queue=queue_name, durable=True)

    # Đặt prefetch_count để kiểm soát số message worker nhận cùng lúc
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    print(f"[*] Waiting for messages in {queue_name}. To exit press CTRL+C")
    channel.start_consuming()

if __name__ == "__main__":
    import threading

    # Chạy worker cho cả 2 queue
    threading.Thread(target=consume, args=("blood_glucose_queue",)).start()
    threading.Thread(target=consume, args=("blood_pressure_queue",)).start()
