from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import RegexValidator

from mongoengine import Document, StringField, FloatField, IntField, DateTimeField, ReferenceField

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('Phone number is required.')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, password, **extra_fields)

class User(AbstractUser):
    username = None  # Delete username field
    
    phone_regex = RegexValidator(
        regex=r'^(0[235789]{1}[0-9]{8})$',
        message=_("Phone number must be a valid Vietnamese number (e.g., 09xxxxxxxx or 03xxxxxxxx).")
    )
    phone_number = models.CharField(
        _('phone number'),
        max_length=12,
        unique=True,
        validators=[phone_regex],  
        error_messages={
            'unique': _("A user with that phone number already exists."),
        },
    )
    
    USERNAME_FIELD = 'phone_number'  # Sử dụng phone_number làm định danh
    REQUIRED_FIELDS = []  # Bỏ các trường bắt buộc khi tạo superuser

    objects = UserManager()

    def __str__(self):
        return self.phone_number


class BloodGlucose(Document):
    """
    A model representing a blood glucose measurement.

    Attributes:
        blood_glucose (float): The blood glucose level.
        unit (str): The unit of the blood glucose measurement, either 'mg/dL' or 'mmol/L'.
        timestamp (datetime): The date and time when the measurement was taken.
        meal (str): The context of the measurement, either 'pre-meal', 'post-meal', 'fasting', or 'before bed'.
    """
    user_id = IntField(required=True)
    blood_glucose = FloatField(required=True)
    unit = StringField(choices=['mg/dL', 'mmol/L'], required=True)
    timestamp = DateTimeField(default=timezone.now, required=True)
    meal = StringField(choices=['pre-meal', 'post-meal', 'fasting', 'before bed'], required=True)

class BloodPressure(Document):
    """
    BloodPressure model to store blood pressure readings.

    Attributes:
        systolic (int): The systolic blood pressure value. This field is required.
        diastolic (int): The diastolic blood pressure value. This field is required.
        timestamp (datetime): The date and time when the blood pressure reading was taken. This field is required.
        unit (str): The unit of measurement for the blood pressure reading. Defaults to 'mm Hg'. This field is required.
    """
    user_id = IntField(required=True)
    systolic = IntField(required=True)
    diastolic = IntField(required=True)
    timestamp = DateTimeField(default=timezone.now, required=True)
    unit = StringField(default='mm Hg', required=True)