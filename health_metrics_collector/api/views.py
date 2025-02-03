from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import status

from .models import BloodGlucose, BloodPressure
from .serializers import (
    BloodGlucoseSerializer,
    BloodPressureSerializer,
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
)
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
        return BloodGlucose.objects.filter(user_id=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)

    def get_object(self):
        """Truy vấn dữ liệu theo ID và user_id"""
        pk = self.kwargs.get("pk")  # Lấy ID từ URL
        try:
            return BloodGlucose.objects.get(id=pk, user_id=self.request.user.id)
        except BloodGlucose.DoesNotExist:
            raise NotFound("Blood Glucose record not found")

    def update(self, request, *args, **kwargs):
        """Cập nhật dữ liệu Blood Glucose"""
        blood_glucose = self.get_object()
        serializer = self.get_serializer(blood_glucose, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Blood glucose record updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        return BloodPressure.objects.filter(user_id=self.request.user.id)
    
    # Save the serializer with the current user as the owner
    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)

    def get_object(self):
        """Truy vấn dữ liệu theo ID và user_id"""
        pk = self.kwargs.get("pk")
        try:
            return BloodPressure.objects.get(id=pk, user_id=self.request.user.id)
        except BloodPressure.DoesNotExist:
            raise NotFound("Blood Pressure record not found")
    
    def update(self, request, *args, **kwargs):
        """Cập nhật dữ liệu Blood Pressure"""
        blood_pressure = self.get_object()
        serializer = self.get_serializer(blood_pressure, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "Blood pressure record updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        print("Access Token:", response.data['access']) 
        print("Refresh Token:", response.data['refresh'])
        return response