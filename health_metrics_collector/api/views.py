from django.shortcuts import render

from rest_framework import generics, permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import UpdateAPIView
from rest_framework.decorators import api_view, permission_classes

from .models import BloodGlucose, BloodPressure
from .serializers import (
    BloodGlucoseSerializer,
    BloodPressureSerializer,
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    UserUpdateSerializer,
    UserUpdatePasswordSerializer,
)
from .permissions import IsOwnerPermission
from .rabbitmq import publish_message

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
        # serializer.save(user_id=self.request.user.id)
        instance = serializer.save(user_id=self.request.user.id)
        
        # Send message to RabbitMQ
        message = {
            "user_id": instance.user_id,
            "blood_glucose": instance.blood_glucose,
            "unit": instance.unit,
            "meal": instance.meal,
        }
        publish_message("blood_glucose_queue", message)

    def get_object(self):
        """Truy vấn dữ liệu theo ID và user_id"""
        pk = self.kwargs.get("pk")  # Lấy ID từ URL
        try:
            return BloodGlucose.objects.get(id=pk, user_id=self.request.user.id)
        except BloodGlucose.DoesNotExist:
            raise NotFound("Blood Glucose record not found")

    def update(self, request, *args, **kwargs):
        blood_glucose = self.get_object()
        serializer = self.get_serializer(blood_glucose, data=request.data, partial=True)
        if serializer.is_valid():
            instance = serializer.save()

            message = {
                "user_id": instance.user_id,
                "blood_glucose": instance.blood_glucose,
                "unit": instance.unit,
                "meal": instance.meal,
            }
            publish_message("blood_glucose_queue", message)

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
        try:
            return BloodPressure.objects.filter(user_id=self.request.user.id)
        except Exception as e:
            raise NotFound(f"Error retrieving blood pressure records: {str(e)}")
    
    # Save the serializer with the current user as the owner
    def perform_create(self, serializer):
        try:
            # serializer.save(user_id=self.request.user.id)
            instance = serializer.save(user_id=self.request.user.id)
            message = {
                "user_id": instance.user_id,
                "systolic": instance.systolic,
                "diastolic": instance.diastolic,
                "timestamp": instance.timestamp.isoformat()
            }
            publish_message("blood_pressure_queue", message)

        except Exception as e:
            return Response({
                "status": "error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_object(self):
        """Truy vấn dữ liệu theo ID và user_id"""
        pk = self.kwargs.get("pk")
        try:
            return BloodPressure.objects.get(id=pk, user_id=self.request.user.id)
        except BloodPressure.DoesNotExist:
            raise NotFound("Blood Pressure record not found")
        except Exception as e:
            raise NotFound(f"Error retrieving blood pressure record: {str(e)}")
    
    def update(self, request, *args, **kwargs):
        """Cập nhật dữ liệu Blood Pressure"""
        try:
            blood_pressure = self.get_object()
            serializer = self.get_serializer(blood_pressure, data=request.data, partial=True)
            if serializer.is_valid():
                # serializer.save()
                instance = serializer.save()
                message = {
                    "user_id": instance.user_id,
                    "systolic": instance.systolic,
                    "diastolic": instance.diastolic,
                    "timestamp": instance.timestamp.isoformat()
                }
                publish_message("blood_pressure_queue", message)

                return Response({
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "Blood pressure record updated successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            print("Access Token:", response.data['access']) 
            print("Refresh Token:", response.data['refresh'])
            return response
        except Exception as e:
            return Response({
                "status": "error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class UserUpdateView(UpdateAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = self.request.user
        # if user.is_deleted:
        #     raise Response({"error": "This user has been deleted."}, status=status.HTTP_404_NOT_FOUND)
        return user

    def update(self, request, *args, **kwargs):
        # Cập nhật thông tin user
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status": "success",
                    "status_code": status.HTTP_200_OK,
                    "message": "User information updated successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "status": "error",
                "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserUpdatePasswordView(UpdateAPIView):
    serializer_class = UserUpdatePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not user.check_password(current_password):
            return Response({
                "status": "error",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Current password is incorrect"
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(user, data={"password": new_password}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "status_code": status.HTTP_200_OK,
                "message": "User password updated successfully",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def soft_delete_user(request):
    """
    Xóa mềm user: đánh dấu is_deleted=True
    Chỉ cho phép user tự xóa tài khoản của mình (hoặc admin có thể làm điều này)
    """
    user = request.user
    try:
        user.is_active = False
        user.save()
        return Response({
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": "User has been soft deleted."
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "status": "error",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def hard_delete_user(request):
    """
    Xóa cứng user: xóa khỏi hệ thống và xóa dữ liệu liên quan.
    Chỉ admin hoặc user có quyền cao mới nên thực hiện.
    """
    user = request.user
    if not user.is_staff:  # Chỉ admin mới có quyền xóa vĩnh viễn
        return Response({"message": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
    try:
        # Xóa dữ liệu sức khỏe liên quan trong MySQL
        BloodGlucose.objects.filter(user_id=user.id).delete()
        BloodPressure.objects.filter(user_id=user.id).delete()
        # Xóa user khỏi cơ sở dữ liệu MySQL (xóa vĩnh viễn)
        user.delete()
        return Response({
            "status": "success",
            "status_code": status.HTTP_200_OK,
            "message": "User and all related health data have been permanently deleted."
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "status": "error",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)