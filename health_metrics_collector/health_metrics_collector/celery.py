import os
from celery import Celery

# Cấu hình Celery với Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "health_metrics_collector.settings")

app = Celery("health_metrics_collector")

# Nạp config từ settings.py, dùng biến có tiền tố "CELERY_"
app.config_from_object("django.conf:settings", namespace="CELERY")

# Tự động tìm task trong tất cả apps của Django
app.autodiscover_tasks()
