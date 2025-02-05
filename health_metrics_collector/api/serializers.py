import datetime

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import BloodGlucose, BloodPressure
import logging

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """This class is used to serialize the User model.

    Args:
        serializers (_type_): _description_
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def create(self, validated_data):
        try:
            # Tạo user mới và hash mật khẩu
            user = User.objects.create_user(**validated_data)
            return user
        except Exception as e:
            # Log the exception
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating user: {e}")
            raise serializers.ValidationError("An error occurred while creating the user.")

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class UserUpdatePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['password']

class BloodGlucoseSerializer(serializers.Serializer):
    """This class is used to serialize the BloodGlucose model.

    Args:
        serializers (_type_): _description_

    Returns:
        _type_: _description_
    """
    id = serializers.CharField(read_only=True)
    blood_glucose = serializers.FloatField()
    unit = serializers.ChoiceField(choices=['mg/dL', 'mmol/L'])
    timestamp = serializers.DateTimeField(read_only=True)
    meal = serializers.ChoiceField(choices=['pre-meal', 'post-meal', 'fasting', 'before bed'])

    def validate_blood_glucose(self, value):
        if value <= 0:
            raise serializers.ValidationError("Blood glucose must be positive.")
        return value
    
    def validate_unit(self, value):
        if value not in ['mg/dL', 'mmol/L']:
            raise serializers.ValidationError("Unit must be 'mg/dL' or 'mmol/L'.")
        return value
    
    def validate_meal(self, value):
        if value not in ['pre-meal', 'post-meal', 'fasting', 'before bed']:
            raise serializers.ValidationError("Meal must be 'pre-meal', 'post-meal', 'fasting', or 'before bed'.")
        return value
    
    def validate_timestamp(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Timestamp cannot be in the future.")
        return value

    def create(self, validated_data):
        try:
            return BloodGlucose.objects.create(**validated_data)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating BloodGlucose record: {e}")
            raise serializers.ValidationError("An error occurred while creating the BloodGlucose record.")

    def update(self, instance, validated_data):
        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            return instance
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating BloodGlucose record: {e}")
            raise serializers.ValidationError("An error occurred while updating the BloodGlucose record.")
    
class BloodPressureSerializer(serializers.Serializer):
    """This class is used to serialize the BloodPressure model.

    Args:
        serializers (_type_): _description_

    Returns:
        _type_: _description_
    """
    id = serializers.CharField(read_only=True)
    systolic = serializers.IntegerField()
    diastolic = serializers.IntegerField()
    timestamp = serializers.DateTimeField(read_only=True)
    unit = serializers.CharField(default='mm Hg')

    def validate_systolic(self, value):
        if value <= 0:
            raise serializers.ValidationError("Systolic blood pressure must be positive.")
        return value
    
    def validate_diastolic(self, value):
        if value <= 0:
            raise serializers.ValidationError("Diastolic blood pressure must be positive.")
        return value
    
    def validate_unit(self, value):
        if value != 'mm Hg':
            raise serializers.ValidationError("Unit must be 'mm Hg'.")
        return value
    
    def validate_timestamp(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Timestamp cannot be in the future.")
        return value

    def create(self, validated_data):
        """This method is used to create a new BloodPressure object.

        Args:
            validated_data (dict): A dictionary containing validated data for creating a BloodPressure object.

        Returns:
            BloodPressure: The newly created BloodPressure object.
        """
        try:
            validated_data['timestamp'] = timezone.now()
            validated_data['unit'] = 'mm Hg'
            return BloodPressure.objects.create(**validated_data)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating BloodPressure record: {e}")
            raise serializers.ValidationError("An error occurred while creating the BloodPressure record.")

    def update(self, instance, validated_data):
        """
        Updates the instance with the provided validated data.

        Args:
            instance (Model): The instance to be updated.
            validated_data (dict): A dictionary containing the validated data to update the instance with.

        Returns:
            Model: The updated instance.
        """
        try:
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            return instance
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating BloodPressure record: {e}")
            raise serializers.ValidationError("An error occurred while updating the BloodPressure record.")
    
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['phone_number', 'password', 'first_name', 'last_name']

        def create(self, validated_data):
            try:
                user = User.objects.create_user(
                    phone_number=validated_data['phone_number'],
                    password=validated_data['password'],
                    first_name=validated_data.get('first_name', ''),
                    last_name=validated_data.get('last_name', ''),
                )
                return user
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.error(f"Error creating user: {e}")
                raise serializers.ValidationError("An error occurred while creating the user.")

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            attrs['username'] = attrs.get('phone_number', '')
            return super().validate(attrs)
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Error validating token: {e}")
            raise serializers.ValidationError("An error occurred while validating the token.")