from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import logging

from services.openfga.sync.utils import sync_relations
from services.openfga.relations import (
    CourseClassRelation,
    UserRelation,
)

from .models import Enrollment, EnrollmentRole

User = get_user_model()
logger = logging.getLogger(__name__)


ENROLLMENT_ROLE_RELATION_MAP = {
    EnrollmentRole.TEACHER: CourseClassRelation.TEACHER,
    EnrollmentRole.STUDENT: CourseClassRelation.STUDENT,
    EnrollmentRole.GUEST: CourseClassRelation.GUEST,
}


@receiver(post_save, sender=Enrollment, dispatch_uid="sync_enrollment_to_fga")
def sync_enrollment_to_fga(sender, instance: Enrollment, created, **kwargs):
    return sync_relations(
        subject_key=f"{UserRelation.TYPE}:{instance.user.pk}",
        desired_relations=set([ENROLLMENT_ROLE_RELATION_MAP[instance.role]]),
        object_key=f"{CourseClassRelation.TYPE}:{instance.course_class.pk}",
    )
