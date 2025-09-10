from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from openfga_sdk.client.models import (
    ClientTuple,
    ClientWriteRequest,
    ClientCheckRequest,
)
import logging

from proxies.openfga.sync import client as fga
from proxies.openfga.relations import (
    CourseClassRelation,
    UserRelation,
)

from .decorators import (
    handle_course_class_postsave_syncing_exceptions,
)
from .models import CourseClass

User = get_user_model()
logger = logging.getLogger(__name__)


def create_course_class_open_for_guest_tuple(class_id):
    return ClientTuple(
        user=f"{UserRelation.TYPE}:*",
        relation=CourseClassRelation.GUEST,
        object=f"{CourseClassRelation.TYPE}:{class_id}",
    )


@receiver(post_save, sender=CourseClass)
@handle_course_class_postsave_syncing_exceptions
def sync_course_class_open_access(sender, instance: CourseClass, created, **kwargs):
    ofga_is_open = fga.check(
        ClientCheckRequest(
            user=f"{UserRelation.TYPE}:*",
            relation=CourseClassRelation.CAN_VIEW,
            object=f"{CourseClassRelation.TYPE}:{instance.id}",
        )
    ).allowed

    # Already synced
    if ofga_is_open == instance.is_open:
        return

    open_access_tuple = create_course_class_open_for_guest_tuple(instance.id)
    if instance.is_open:
        # Make it open
        return fga.write(ClientWriteRequest(writes=[open_access_tuple]))
    # Make it closed
    return fga.write(ClientWriteRequest(deletes=[open_access_tuple]))
