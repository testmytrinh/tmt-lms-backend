from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from itsdangerous import URLSafeTimedSerializer


class MyUserManager(BaseUserManager):
    def create_user(self, email: str, password: str, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        user: User = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        user = self.create_user(email=email, password=password, **extra_fields)
        return user


class User(AbstractUser):
    username = None
    email = models.EmailField("email address", unique=True)
    avatar = models.CharField(max_length=255, blank=False, null=True)
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = MyUserManager()

    # @property
    # def avatar_url(self):
    #     return f"https://{settings.CLOUDFRONT_DOMAIN}/{self.avatar}"

    def generate_activation_token(self, salt="account-activation-salt"):
        s = URLSafeTimedSerializer(settings.SECRET_KEY, salt=salt)
        return s.dumps({"pk": self.pk})

    def __str__(self):
        return f"{self.email}|{self.get_full_name()}"
