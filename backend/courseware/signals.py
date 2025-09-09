from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from openfga_sdk.models.fga_object import FgaObject
from openfga_sdk.client.models import ClientTuple, ClientWriteRequest
from openfga_sdk.client.models.list_users_request import (
    ClientListUsersRequest,
    UserTypeFilter,
)
from openfga_sdk import ReadRequestTupleKey
import logging

from proxies.openfga.sync import client as fga
from proxies.openfga.relations import (
    CourseTemplateRelation,
    UserRelation,
)

from .decorators import handle_template_postsave_syncing_exceptions
from .models import CourseTemplate

User = get_user_model()
logger = logging.getLogger(__name__)


def create_template_owner_tuple(template_id, owner_id):
    return ClientTuple(
        user=f"{UserRelation.TYPE}:{owner_id}",
        relation=CourseTemplateRelation.OWNER,
        object=f"{CourseTemplateRelation.TYPE}:{template_id}",
    )


@receiver(post_save, sender=CourseTemplate)
@handle_template_postsave_syncing_exceptions
def sync_template_ownership(sender, instance, created, **kwargs):
    """Sync course template ownership to OpenFGA"""
    ofga_template_owners = ClientListUsersRequest(
        object=FgaObject(type=CourseTemplateRelation.TYPE, id=str(instance.id)),
        relation=CourseTemplateRelation.OWNER,
        user_filters=[UserTypeFilter(type=UserRelation.TYPE)],
    ).users

    # I gotta convert these into sets cuz ofga returns list
    ofga_template_owner_ids = set(int(user.id) for user in ofga_template_owners)
    owner_id = set([int(instance.id)])

    to_add = owner_id - ofga_template_owner_ids
    to_del = ofga_template_owner_ids - owner_id

    payload = {}
    if to_add:
        payload["writes"] = [
            create_template_owner_tuple(instance.id, uid) for uid in to_add
        ]
    if to_del:
        payload["deletes"] = [
            create_template_owner_tuple(instance.id, uid) for uid in to_del
        ]
    if not payload:
        return
    return fga.write(ClientWriteRequest(**payload))


@receiver(post_delete, sender=CourseTemplate)
def remove_template_from_openfga(sender, instance, **kwargs):
    """Remove template permissions from OpenFGA when deleted"""
    try:
        if instance.owner:
            # Read all tuples for this template and delete them
            read_response = fga.read(
                ReadRequestTupleKey(
                    object=f"{CourseTemplateRelation.TYPE}:{instance.id}"
                )
            )
            tuples_to_delete = []

            for tuple_obj in read_response.tuples:
                key = tuple_obj.key
                tuples_to_delete.append(
                    ClientTuple(user=key.user, relation=key.relation, object=key.object)
                )

            if tuples_to_delete:
                fga.write(ClientWriteRequest(deletes=tuples_to_delete))
                logger.info(
                    f"Removed {len(tuples_to_delete)} template permissions from OpenFGA"
                )
            else:
                logger.info("No template permissions found to remove from OpenFGA")
    except Exception as e:
        logger.error(f"Error removing template permissions from OpenFGA: {e}")
