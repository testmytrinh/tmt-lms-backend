from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from openfga_sdk.client.models import ClientTuple, ClientWriteRequest
from openfga_sdk import ReadRequestTupleKey
import logging

from proxies.openfga.sync import client as fga
from proxies.openfga.relations import (
    CourseClassRelation,
    GroupRelation,
    UserRelation,
)

from .models import Enrollment, EnrollmentRole

User = get_user_model()
logger = logging.getLogger(__name__)


ENROLLMENT_ROLE_TO_COURSE_CLASS = {
    EnrollmentRole.TEACHER: CourseClassRelation.TEACHER,
    EnrollmentRole.STUDENT: CourseClassRelation.STUDENT,
    EnrollmentRole.GUEST: CourseClassRelation.GUEST,
}


@receiver(post_save, sender=Enrollment)
def sync_enrollment_to_openfga(sender, instance, created, **kwargs):
    """Sync enrollment changes to OpenFGA"""
    try:
        role_relation = ENROLLMENT_ROLE_TO_COURSE_CLASS[instance.role]
        tuple_obj = ClientTuple(
            user=f"{UserRelation.TYPE}:{instance.user.id}",
            relation=role_relation,
            object=f"{CourseClassRelation.TYPE}:{instance.course_class.id}",
        )

        if created:
            # New enrollment
            fga.write(ClientWriteRequest(writes=[tuple_obj]))
            logger.info(
                f"Synced new enrollment {instance.user.email} -> {instance.course_class} to OpenFGA"
            )
            return
        elif hasattr(instance, "_old_role") and instance._old_role != instance.role:
            # Role changed - need to remove old and add new
            old_role_relation = ENROLLMENT_ROLE_TO_COURSE_CLASS[instance._old_role]
            old_tuple = ClientTuple(
                user=f"{UserRelation.TYPE}:{instance.user.id}",
                relation=old_role_relation,
                object=f"{CourseClassRelation.TYPE}:{instance.course_class.id}",
            )

            fga.write(ClientWriteRequest(deletes=[old_tuple], writes=[tuple_obj]))
            logger.info(
                f"Synced enrollment role change {instance.user.email} -> {instance.course_class.name} to OpenFGA"
            )

    except Exception as e:
        logger.error(f"Error syncing enrollment to OpenFGA: {e}")


@receiver(post_delete, sender=Enrollment)
def remove_enrollment_from_openfga(sender, instance, **kwargs):
    """Remove enrollment from OpenFGA when deleted"""
    try:
        role_relation = ENROLLMENT_ROLE_TO_COURSE_CLASS[instance.role]

        tuple_obj = ClientTuple(
            user=f"{UserRelation.TYPE}:{instance.user.id}",
            relation=role_relation,
            object=f"{CourseClassRelation.TYPE}:{instance.course_class.id}",
        )

        fga.write(ClientWriteRequest(deletes=[tuple_obj]))
        logger.info(
            f"Removed enrollment {instance.user.email} -> {instance.course_class.name} from OpenFGA"
        )
    except Exception as e:
        logger.error(f"Error removing enrollment from OpenFGA: {e}")
