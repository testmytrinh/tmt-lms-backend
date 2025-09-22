from django.contrib.auth import get_user_model
from django.conf import settings
from itsdangerous import URLSafeTimedSerializer


User = get_user_model()


def get_all_users():
    return User.objects.all()


def get_active_users():
    return User.objects.filter(is_active=True)


def get_user_pk_from_token(token, max_age=3600):
    """
    Get user's pk from token.
    - If the token is invalid raises :exec:`BadSignature`.
    - If the token is expired raise :exc:`SignatureExpired`."""
    s = URLSafeTimedSerializer(settings.SECRET_KEY)
    return s.loads(token, max_age=max_age, salt="account-activation-salt")["pk"]


def get_inactive_user_by_activation_token(token, max_age=3600):
    try:
        pk = get_user_pk_from_token(token, max_age=max_age)
        return User.objects.get(pk=pk, is_active=False)
    except Exception:
        return None
