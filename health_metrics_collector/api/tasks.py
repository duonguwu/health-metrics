from celery import shared_task
from celery.exceptions import Reject

import logging

from mongoengine import DoesNotExist
from datetime import datetime

from .models import BloodPressure, BloodGlucose
from django.utils import timezone

@shared_task(bind=True, acks_late=True)
def process_blood_pressure(self, data_batch):
    """
    Xử lý dữ liệu huyết áp từ hàng đợi RabbitMQ.
    """
    try:
        print("process_blood_pressure")
        records = []
        for data in data_batch:
            data['timestamp'] = timezone.now().isoformat()
            data['unit'] = 'mm Hg'
            record = BloodPressure(
                user_id=data["user_id"],
                systolic=data["systolic"],
                diastolic=data["diastolic"],
                timestamp=datetime.fromisoformat(data["timestamp"]),
                unit=data.get("unit", "mm Hg"),
            )
            records.append(record)

        # Lưu tất cả bản ghi vào MongoDB trong một lần
        if records:
            BloodPressure.objects.insert(records)

        logging.info(f"✅ Saved {len(records)} BloodPressure records to MongoDB.")
        return f"Saved {len(records)} records"

    except Exception as e:
        logging.error(f"❌ Error saving to MongoDB: {e}")
        raise self.retry(exc=e, countdown=10, max_retries=3)  # Nếu lỗi, thử lại 3 lần
    

@shared_task(bind=True, acks_late=True)
def process_blood_glucose(self, data_batch):
    """
    Xử lý dữ liệu đường huyết từ hàng đợi RabbitMQ.
    """
    try:
        print("process_blood_glucose")
        records = []
        for data in data_batch:
            data['timestamp'] = timezone.now().isoformat()
            data['unit'] = 'mg/dL'
            record = BloodGlucose(
                user_id=data["user_id"],
                glucose_level=data["glucose_level"],
                timestamp=datetime.fromisoformat(data["timestamp"]),
                unit=data.get("unit", "mg/dL"),
            )
            records.append(record)

        # Lưu tất cả bản ghi vào MongoDB trong một lần
        if records:
            BloodGlucose.objects.insert(records)

        logging.info(f"✅ Đã lưu {len(records)} bản ghi BloodGlucose vào MongoDB.")
        return f"Saved {len(records)} records"

    except Exception as e:
        logging.error(f"❌ Lỗi khi lưu vào MongoDB: {e}")
        raise self.retry(exc=e, countdown=10, max_retries=3)  # Nếu lỗi, thử lại 3 lần