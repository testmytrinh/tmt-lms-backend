from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from openfga_sdk.client.models import (
    ClientTuple,
    ClientWriteRequest,
    ClientListObjectsRequest,
)
import logging

from proxies.openfga.sync import client as fga
from proxies.openfga.relations import (
    GroupRelation,
    UserRelation,
)

from .decorators import (
    handle_user_postsave_syncing_exceptions,
    handle_user_m2m_changed_syncing_exceptions,
)

logger = logging.getLogger(__name__)

User = get_user_model()


def create_user_group_member_tuple(user_id, group_id):
    return ClientTuple(
        user=f"{UserRelation.TYPE}:{user_id}",
        relation=GroupRelation.MEMBER,
        object=f"{GroupRelation.TYPE}:{group_id}",
    )


def create_user_list_groups_request(user_id):
    return ClientListObjectsRequest(
        user=f"{UserRelation.TYPE}:{user_id}",
        relation=GroupRelation.MEMBER,
        type=GroupRelation.TYPE,
    )


@receiver(post_save, sender=User)
@handle_user_postsave_syncing_exceptions
def sync_user_groups_on_created(sender, instance, created, **kwargs):
    if not created:
        return
    groups = instance.groups.all()
    if not groups:
        return
    tuples = [create_user_group_member_tuple(instance.id, group.id) for group in groups]
    return fga.write(ClientWriteRequest(writes=tuples))


@receiver(m2m_changed, sender=User.groups.through)
@handle_user_m2m_changed_syncing_exceptions
def sync_user_groups_on_changed(
    sender, instance, action, reverse, model, pk_set, **kwargs
):
    if action not in ["post_add", "post_remove", "post_clear"]:
        return
    desired_group_ids = set(instance.groups.values_list("id", flat=True))
    curr_group_response: list[str] = fga.list_objects(
        create_user_list_groups_request(instance.id)
    ).objects
    curr_group_ids = set(
        int(obj.removeprefix(f"{GroupRelation.TYPE}:")) for obj in curr_group_response
    )
    to_add_group_ids = desired_group_ids - curr_group_ids
    to_del_group_ids = curr_group_ids - desired_group_ids

    payload = {}
    if to_add_group_ids:
        payload["writes"] = [
            create_user_group_member_tuple(instance.id, gr_id)
            for gr_id in to_add_group_ids
        ]
    if to_del_group_ids:
        payload["deletes"] = [
            create_user_group_member_tuple(instance.id, gr_id)
            for gr_id in to_del_group_ids
        ]
    if not payload:
        return
    return fga.write(ClientWriteRequest(**payload))
