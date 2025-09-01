from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenRefreshSerializer,
    TokenBlacklistSerializer,
)
from rest_framework_simplejwt.exceptions import InvalidToken

from .models import User


class CookieTokenRefreshSerializer(TokenRefreshSerializer):
    refresh = None

    def validate(self, attrs):
        attrs["refresh"] = self.context["request"].COOKIES.get("refresh_token")
        if attrs["refresh"]:
            return super().validate(attrs)
        raise InvalidToken("No valid token found in cookie 'refresh_token'")


class CookieTokenBlacklistSerializer(TokenBlacklistSerializer):
    refresh = None

    def validate(self, attrs: dict):
        attrs["refresh"] = self.context["request"].COOKIES.get("refresh_token")
        if attrs["refresh"]:
            return super().validate(attrs)
        raise InvalidToken("No valid token found in cookie 'refresh_token'")


class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "avatar"]
        read_only_fields = fields


class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "password"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }


class UserUpdateSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "avatar",
            "current_password",
            "new_password",
        ]

    def validate_current_password(self, value):
        user: User = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        current_password = self.initial_data.get("current_password")
        if value and not current_password:
            raise serializers.ValidationError(
                "New password must be provided with current password."
            )
        # Gotta validate the new password for security reasons
        # Like: length, capital letters, ...
        validate_password(value)
        return value

    def update(self, instance, validated_data):
        if "new_password" in validated_data:
            password = validated_data.pop("new_password")
            instance.set_password(password)
            instance.save()
        return super().update(instance, validated_data)
