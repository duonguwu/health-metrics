from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import BloodGlucose, BloodPressure

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """This class is used to serialize the User model.

    Args:
        serializers (_type_): _description_
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

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
    timestamp = serializers.DateTimeField()
    meal = serializers.ChoiceField(choices=['pre-meal', 'post-meal', 'fasting', 'before bed'])

    def create(self, validated_data):
        return BloodGlucose.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
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
    timestamp = serializers.DateTimeField()
    unit = serializers.CharField(default='mm Hg')

    def create(self, validated_data):
        """This method is used to create a new BloodPressure object.

        Args:
            validated_data (dict): A dictionary containing validated data for creating a BloodPressure object.

        Returns:
            BloodPressure: The newly created BloodPressure object.
        """
        return BloodPressure.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Updates the instance with the provided validated data.

        Args:
            instance (Model): The instance to be updated.
            validated_data (dict): A dictionary containing the validated data to update the instance with.

        Returns:
            Model: The updated instance.
        """
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance