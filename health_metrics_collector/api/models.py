from django.contrib.auth.models import AbstractUser
from django.db import models
from mongoengine import Document, StringField, FloatField, IntField, DateTimeField, EnumField


class User(AbstractUser):
    pass

class BloodGlucose(Document):
    """
    A model representing a blood glucose measurement.

    Attributes:
        blood_glucose (float): The blood glucose level.
        unit (str): The unit of the blood glucose measurement, either 'mg/dL' or 'mmol/L'.
        timestamp (datetime): The date and time when the measurement was taken.
        meal (str): The context of the measurement, either 'pre-meal', 'post-meal', 'fasting', or 'before bed'.
    """
    blood_glucose = FloatField(required=True)
    unit = StringField(choices=['mg/dL', 'mmol/L'], required=True)
    timestamp = DateTimeField(required=True)
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
    systolic = IntField(required=True)
    diastolic = IntField(required=True)
    timestamp = DateTimeField(required=True)
    unit = StringField(default='mm Hg', required=True)