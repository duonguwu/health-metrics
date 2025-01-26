from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import BloodGlucose, BloodPressure
from .serializers import BloodGlucoseSerializer, BloodPressureSerializer
from .permissions import IsOwnerPermission

class BloodGlucoseViewSet(ModelViewSet):
    """
    A viewset for viewing and editing blood glucose instances.

    Attributes:
        serializer_class (BloodGlucoseSerializer): The serializer class used for the viewset.
        permission_classes (list): The list of permission classes that are used to determine access.

    Methods:
        get_queryset():
            Returns the queryset of BloodGlucose objects filtered by the current user.
        
        perform_create(serializer):
            Saves the serializer with the current user as the owner.
    """
    serializer_class = BloodGlucoseSerializer
    permission_classes = [IsAuthenticated, IsOwnerPermission]

    # Return data of user who is logged in
    def get_queryset(self):
        return BloodGlucose.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BloodPressureViewSet(ModelViewSet):
    """
    A viewset for viewing and editing blood pressure instances.
    Attributes:
        serializer_class (BloodPressureSerializer): The serializer class used for the viewset.
        permission_classes (list): A list of permission classes that are used to determine access control.
    Methods:
        get_queryset():
            Returns the queryset of blood pressure instances for the currently authenticated user.
        perform_create(serializer):
            Saves the serializer with the current user as the owner.
    """
    serializer_class = BloodPressureSerializer
    permission_classes = [IsAuthenticated, IsOwnerPermission]

    # Return data of user who is logged in
    def get_queryset(self):
        return BloodPressure.objects.filter(user=self.request.user)
    
    # Save the serializer with the current user as the owner
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)