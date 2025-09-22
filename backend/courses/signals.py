from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import logging

from services.openfga.sync.utils import (
    delete_all_subject_tuples,
    sync_single_type_subjects,
)

from services.openfga.relations import (
    CourseClassRelation,
    UserRelation,
)

from .decorators import handle_course_class_postsave_syncing_exceptions
from .models import CourseClass

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=CourseClass, dispatch_uid="sync_course_class_open_access")
@handle_course_class_postsave_syncing_exceptions
def sync_course_class_open_access(sender, instance: CourseClass, created, **kwargs):
    logger.info(
        f"Syncing CourseClass (id={instance.id}) open access status to OpenFGA. Created: {created}"
    )
    return sync_single_type_subjects(
        object_key=f"{CourseClassRelation.TYPE}:{instance.id}",
        subject_type=UserRelation.TYPE,
        relation=CourseClassRelation.CAN_VIEW,
        desired_subject_ids=set(["*"]) if instance.is_open else set(),
    )


@receiver(post_delete, sender=CourseClass, dispatch_uid="cleanup_course_class_in_ofga")
def cleanup_course_class_in_ofga(sender, instance: CourseClass, **kwargs):
    logger.info(f"Cleaning up CourseClass (id={instance.id}) from OpenFGA on deletion.")
    delete_all_subject_tuples(object_key=f"{CourseClassRelation.TYPE}:{instance.id}")
