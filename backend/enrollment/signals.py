from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from openfga_sdk.client.models import ClientTuple
import logging

from proxies.openfga.sync.utils import sync_relations
from proxies.openfga.relations import (
    CourseClassRelation,
    UserRelation,
)

from .decorators import handle_enrollment_postsave_syncing_exceptions
from .models import Enrollment, EnrollmentRole

User = get_user_model()
logger = logging.getLogger(__name__)


ENROLLMENT_ROLE_RELATION_MAP = {
    EnrollmentRole.TEACHER: CourseClassRelation.TEACHER,
    EnrollmentRole.STUDENT: CourseClassRelation.STUDENT,
    EnrollmentRole.GUEST: CourseClassRelation.GUEST,
}


@receiver(post_save, sender=Enrollment)
@handle_enrollment_postsave_syncing_exceptions
def sync_enrollment_to_fga(sender, instance: Enrollment, created, **kwargs):
    if instance.role == EnrollmentRole.GUEST and instance.course_class.is_open:
        return
    return sync_relations(
        subject_key=f"{UserRelation.TYPE}:{instance.user.id}",
        desired_relations=set([ENROLLMENT_ROLE_RELATION_MAP[instance.role]]),
        object_key=f"{CourseClassRelation.TYPE}:{instance.course_class.id}",
    )
