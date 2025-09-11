from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import logging

from proxies.openfga.sync.utils import (
    sync_subjects,
    sync_objects,
    delete_all_subject_tuples,
)

from proxies.openfga.relations import (
    CourseClassRelation,
    CourseTemplateRelation,
    UserRelation,
)

from .decorators import handle_course_class_postsave_syncing_exceptions
from .models import CourseClass

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=CourseClass)
@handle_course_class_postsave_syncing_exceptions
def sync_course_class_open_access(sender, instance: CourseClass, created, **kwargs):
    return sync_subjects(
        object_key=f"{CourseClassRelation.TYPE}:{instance.id}",
        subject_type=UserRelation.TYPE,
        relation=CourseClassRelation.GUEST,
        desired_subject_ids=set(["*"]) if instance.is_open else set(),
    )


@receiver(post_save, sender=CourseClass)
@handle_course_class_postsave_syncing_exceptions
def sync_course_class_template(sender, instance: CourseClass, created, **kwargs):
    return sync_objects(
        subject_key=f"{CourseClassRelation.TYPE}:{instance.id}",
        relation=CourseTemplateRelation.COURSE_CLASS,
        object_type=CourseTemplateRelation.TYPE,
        desired_object_ids=set([str(instance.course_template.id)])
        if instance.course_template
        else set(),
    )


@receiver(post_delete, sender=CourseClass)
def cleanup_course_class_relations(sender, instance: CourseClass, **kwargs):
    delete_all_subject_tuples(object_key=f"{CourseClassRelation.TYPE}:{instance.id}")
    # Remove any template linkage tuples
    sync_objects(
        subject_key=f"{CourseClassRelation.TYPE}:{instance.id}",
        relation=CourseTemplateRelation.COURSE_CLASS,
        object_type=CourseTemplateRelation.TYPE,
        desired_object_ids=set(),
    )
