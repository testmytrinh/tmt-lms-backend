from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import TokenVerifyView
from user.views import (
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
    CookieTokenBlacklistView,
    UserViewSet,
)

router = DefaultRouter()

router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/token/blacklist/", CookieTokenBlacklistView.as_view(), name="token_blacklist"),
    path("api/", include(router.urls)),
]
