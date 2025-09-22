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
    ContentNodeRelation,
)

from .models import ContentNode

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=ContentNode, dispatch_uid="sync_node_course_class_in_fga")
def sync_node_course_class_in_fga(sender, instance: ContentNode, created, **kwargs):
    desired_subject_ids = (
        {str(instance.course_class_id)} if instance.course_class_id else set()
    )
    return sync_single_type_subjects(
        object_key=f"{ContentNodeRelation.TYPE}:{instance.id}",
        subject_type=CourseClassRelation.TYPE,
        relation=ContentNodeRelation.COURSE_CLASS,
        desired_subject_ids=desired_subject_ids,
    )


@receiver(post_save, sender=ContentNode, dispatch_uid="sync_node_parent_in_fga")
def sync_node_parent_in_fga(sender, instance: ContentNode, created, **kwargs):
    """Ensure each ContentNode has at most one parent relation in OpenFGA."""
    desired_parent_ids = {str(instance.parent_id)} if instance.parent_id else set()
    return sync_single_type_subjects(
        object_key=f"{ContentNodeRelation.TYPE}:{instance.id}",
        subject_type=ContentNodeRelation.TYPE,
        relation=ContentNodeRelation.PARENT,
        desired_subject_ids=desired_parent_ids,
    )


@receiver(post_delete, sender=ContentNode, dispatch_uid="cleanup_node_in_fga")
def cleanup_node_in_fga(sender, instance: ContentNode, **kwargs):
    return delete_all_subject_tuples(f"{ContentNodeRelation.TYPE}:{instance.id}")
