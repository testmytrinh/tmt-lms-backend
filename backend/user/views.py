from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAdminUser,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
)

# from config.models import Config
from .permissions import IsSelf
from .serializers import (
    CookieTokenBlacklistSerializer,
    CookieTokenRefreshSerializer,
    UserReadSerializer,
    UserRegistrationSerializer,
    UserUpdateSerializer,
)

User = get_user_model()


class CookieTokenObtainPairView(TokenObtainPairView):
    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get("refresh"):
            cookie_max_age = 3600 * 24 * 14  # 14 days
            response.set_cookie(
                "refresh_token",
                response.data["refresh"],
                max_age=cookie_max_age,
                httponly=True,
                samesite="None",
                secure=True,
            )
            del response.data["refresh"]
        return super().finalize_response(request, response, *args, **kwargs)


class CookieTokenRefreshView(TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get("refresh"):
            cookie_max_age = 3600 * 24 * 14  # 14 days
            response.set_cookie(
                "refresh_token",
                response.data["refresh"],
                max_age=cookie_max_age,
                httponly=True,
                samesite="None",
                secure=True,
            )
            del response.data["refresh"]
        return super().finalize_response(request, response, *args, **kwargs)


class CookieTokenBlacklistView(TokenBlacklistView):
    serializer_class = CookieTokenBlacklistSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        response.delete_cookie("refresh_token")
        return super().finalize_response(request, response, *args, **kwargs)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        SERIALIZER_MAP = {
            "list": UserReadSerializer,
            "retrieve": UserReadSerializer,
            "create": UserRegistrationSerializer,
            "update": UserUpdateSerializer,
            "partial_update": UserUpdateSerializer,
            "destroy": UserUpdateSerializer,
        }
        return SERIALIZER_MAP.get(self.action, UserReadSerializer)

    def get_permissions(self):
        PERMISSION_MAP = {
            "list": [IsAuthenticatedOrReadOnly],
            "retrieve": [IsAuthenticatedOrReadOnly],
            "create": [AllowAny],
            "update": [IsAuthenticated, IsSelf | IsAdminUser],
            "partial_update": [IsAuthenticated, IsSelf | IsAdminUser],
            "destroy": [IsAuthenticated, IsSelf | IsAdminUser],
            "me": [IsAuthenticated],
        }
        permission_classes = PERMISSION_MAP.get(self.action, [])
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        return super().perform_create(serializer)

    @action(detail=False, methods=["get"])
    def me(self, request):
        return Response(self.get_serializer(request.user).data, status=200)
