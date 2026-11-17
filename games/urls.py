from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CurrentUserProfileView,
    GameViewSet,
    LoginView,
    RegisterView,
)

router = DefaultRouter()
router.register(r'games', GameViewSet, basename='game')

urlpatterns = [
    # Authentication & API Key Management
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/token/', LoginView.as_view(), name='auth-token'),
    path('auth/me/', CurrentUserProfileView.as_view(), name='auth-me'),

    # Game API endpoints
    path('', include(router.urls)),
]
