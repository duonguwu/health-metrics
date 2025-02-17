import os
from celery import Celery

# Cấu hình Celery với Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "health_metrics_collector.settings")

app = Celery("health_metrics_collector")

# Nạp config từ settings.py, dùng biến có tiền tố "CELERY_"
app.config_from_object("django.conf:settings", namespace="CELERY")

# Tự động tìm task trong tất cả apps của Django
app.autodiscover_tasks()

app.conf.update(
    task_acks_late=True,  # Đảm bảo chỉ ACK sau khi xử lý xong
    worker_prefetch_multiplier=1,  # Mỗi worker chỉ lấy 1 task để tránh overload
    task_reject_on_worker_lost=True,  # Trả lại task nếu worker bị mất kết nối
    broker_heartbeat=10  # Kiểm tra kết nối với RabbitMQ mỗi 10s
)
