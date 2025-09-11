from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
import logging

from proxies.openfga.sync.utils import sync_subjects, delete_all_subject_tuples
from proxies.openfga.relations import (
    CourseTemplateRelation,
    UserRelation,
    TemplateNodeRelation,
)

from .decorators import handle_template_postsave_syncing_exceptions
from .models import CourseTemplate, TemplateNode

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=CourseTemplate)
@handle_template_postsave_syncing_exceptions
def sync_template_ownership(sender, instance, created, **kwargs):
    return sync_subjects(
        object_key=f"{CourseTemplateRelation.TYPE}:{instance.id}",
        subject_type=UserRelation.TYPE,
        relation=CourseTemplateRelation.OWNER,
        desired_subject_ids=set([str(instance.owner.id)]) if instance.owner else set(),
    )


@receiver(post_save, sender=TemplateNode)
@handle_template_postsave_syncing_exceptions
def sync_node_template(sender, instance: TemplateNode, created, **kwargs):
    return sync_subjects(
        object_key=f"{TemplateNodeRelation.TYPE}:{instance.id}",
        subject_type=CourseTemplateRelation.TYPE,
        relation=TemplateNodeRelation.TEMPLATE,
        desired_subject_ids=set([str(instance.course_template.id)])
        if instance.course_template
        else set(),
    )


@receiver(post_save, sender=TemplateNode)
@handle_template_postsave_syncing_exceptions
def sync_node_parent(sender, instance: TemplateNode, created, **kwargs):
    return sync_subjects(
        object_key=f"{TemplateNodeRelation.TYPE}:{instance.id}",
        subject_type=TemplateNodeRelation.TYPE,
        relation=TemplateNodeRelation.PARENT_NODE,
        desired_subject_ids=set([str(instance.parent.id)])
        if instance.parent
        else set(),
    )


@receiver(post_delete, sender=CourseTemplate)
def cleanup_course_template_relations(sender, instance: CourseTemplate, **kwargs):
    return delete_all_subject_tuples(
        object_key=f"{CourseTemplateRelation.TYPE}:{instance.id}"
    )


@receiver(post_delete, sender=TemplateNode)
def cleanup_template_node_relations(sender, instance: TemplateNode, **kwargs):
    return delete_all_subject_tuples(
        object_key=f"{TemplateNodeRelation.TYPE}:{instance.id}"
    )
