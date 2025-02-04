from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from .views import (
    BloodGlucoseViewSet,
    BloodPressureViewSet,
    UserRegistrationView,
    CustomTokenObtainPairView,
    UserUpdateView,
    soft_delete_user,
    hard_delete_user,
)

router = DefaultRouter()
router.register(r'glucose', BloodGlucoseViewSet, basename='glucose')
router.register(r'pressure', BloodPressureViewSet, basename='pressure')

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path("user/update/", UserUpdateView.as_view(), name="user-update"),
    path("user/soft-delete/", soft_delete_user, name="user-soft-delete"),
    path("user/hard-delete/", hard_delete_user, name="user-hard-delete"),
]
