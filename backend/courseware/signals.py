from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import logging

from services.openfga.relations import (
    UserRelation,
)

from .decorators import handle_template_postsave_syncing_exceptions
from .models import ContentNode

User = get_user_model()
logger = logging.getLogger(__name__)
