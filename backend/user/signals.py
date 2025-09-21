from django.contrib.auth import get_user_model
from django.db.models.signals import m2m_changed, pre_delete
from django.dispatch import receiver
from functools import partial
from openfga_sdk.client.models import (
    ClientTuple,
    ClientWriteRequest,
)
import logging

from services.openfga.relations import (
    UserRelation,
    GroupRelation,
)
from services.openfga.sync import client as fga

logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(
    m2m_changed, sender=User.groups.through, dispatch_uid="sync_user_groups_on_changed"
)
def sync_user_groups_on_changed(
    sender, instance, action, reverse, model, pk_set, **kwargs
):
    if action not in ["post_add", "post_remove"]:
        return
    make_tuple = partial(
        ClientTuple,
        user=f"{UserRelation.TYPE}:{instance.pk}",
        relation=GroupRelation.MEMBER,
    )
    tuples = [make_tuple(object=f"{GroupRelation.TYPE}:{id}") for id in pk_set]
    return fga.write(
        ClientWriteRequest(
            writes=tuples if action == "post_add" else None,
            deletes=tuples if action == "post_remove" else None,
        )
    )


@receiver(pre_delete, sender=User, dispatch_uid="cleanup_user_in_fga")
def cleanup_user_in_fga(sender, instance, **kwargs):
    make_tuple = partial(ClientTuple, user=f"{UserRelation.TYPE}:{instance.pk}")

    # Clean group memberships
    group_ids = instance.groups.values_list("id", flat=True)
    fga.write(
        ClientWriteRequest(
            deletes=[
                make_tuple(
                    object=f"{GroupRelation.TYPE}:{id}", relation=GroupRelation.MEMBER
                )
                for id in group_ids
            ]
        )
    )
