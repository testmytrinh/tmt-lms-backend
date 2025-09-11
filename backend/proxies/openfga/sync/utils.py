from openfga_sdk import ReadRequestTupleKey
from openfga_sdk.client.models import (
    ClientWriteRequest,
    ClientTuple,
)

from . import client


def flush_all_tuples():
    read_response = client.read(ReadRequestTupleKey())
    todelete_tuples = []

    for tuple_obj in read_response.tuples:
        key = tuple_obj.key
        todelete_tuples.append(
            ClientTuple(user=key.user, relation=key.relation, object=key.object)
        )

    if todelete_tuples:
        delete_request = ClientWriteRequest(deletes=todelete_tuples)
        return client.write(delete_request)
    return


def sync_subjects(
    object_key: str, subject_type: str, relation: str, desired_subject_ids: set[str]
):
    """
    This func will sync the subjects of a given object+relation to match the desired_subject_ids.
    It will add missing subjects in desired_subject_ids and remove subjects not in desired_subject_ids.
    Note: this only works with raw relationships, not computed ones.
    THIS WONT WORK FOR MULTI-TYPE SUBJECT relation
    """
    if not object_key or not subject_type or not relation:
        raise ValueError("object_key, subject_type and relation are required")

    existing_subject_tuples = client.read(
        ReadRequestTupleKey(
            object=object_key,
            relation=relation,
        )
    ).tuples
    existing_subject_ids: set[str] = set(
        t.key.user.removeprefix(f"{subject_type}:") for t in existing_subject_tuples
    )

    to_add_subject_ids = desired_subject_ids - existing_subject_ids
    to_del_subject_ids = existing_subject_ids - desired_subject_ids

    payload = {}
    if to_add_subject_ids:
        payload["writes"] = [
            ClientTuple(
                user=f"{subject_type}:{id}", relation=relation, object=object_key
            )
            for id in to_add_subject_ids
        ]
    if to_del_subject_ids:
        payload["deletes"] = [
            ClientTuple(
                user=f"{subject_type}:{id}", relation=relation, object=object_key
            )
            for id in to_del_subject_ids
        ]
    if not payload:
        return
    return client.write(ClientWriteRequest(**payload))


def sync_objects(
    subject_key: str,
    object_type: str,
    relation: str,
    desired_object_ids: set[str],
):
    """
    This func will sync the objects of a given subject+relation to match the desired_object_ids.
    It will add missing objects in desired_object_ids and remove objects not in desired_object_ids.
    Note: this only works with raw relationships, not computed ones.
    THIS WONT WORK FOR MULTI-TYPE OBJECT relation
    """
    if not object_type or not subject_key or not relation:
        raise ValueError("object_type, subject_key and relation are required")

    existing_object_tuples = client.read(
        ReadRequestTupleKey(
            user=subject_key,
            relation=relation,
            object=f"{object_type}:",
        )
    ).tuples
    existing_object_ids: set[str] = set(
        t.key.object.removeprefix(f"{object_type}:") for t in existing_object_tuples
    )

    to_add_object_ids = desired_object_ids - existing_object_ids
    to_del_object_ids = existing_object_ids - desired_object_ids

    payload = {}
    if to_add_object_ids:
        payload["writes"] = [
            ClientTuple(
                user=subject_key, relation=relation, object=f"{object_type}:{id}"
            )
            for id in to_add_object_ids
        ]
    if to_del_object_ids:
        payload["deletes"] = [
            ClientTuple(
                user=subject_key, relation=relation, object=f"{object_type}:{id}"
            )
            for id in to_del_object_ids
        ]
    if not payload:
        return
    return client.write(ClientWriteRequest(**payload))


def sync_relations(
    subject_key: str,
    object_key: str,
    desired_relations: set[str],
):
    if not subject_key or not object_key:
        raise ValueError("subject_key and object_key are required")

    existing_tuples = client.read(
        ReadRequestTupleKey(
            user=subject_key,
            object=object_key,
        )
    ).tuples
    existing_relations: set[str] = set(t.key.relation for t in existing_tuples)

    to_add_relations = desired_relations - existing_relations
    to_del_relations = existing_relations - desired_relations

    payload = {}
    if to_add_relations:
        payload["writes"] = [
            ClientTuple(user=subject_key, relation=relation, object=object_key)
            for relation in to_add_relations
        ]
    if to_del_relations:
        payload["deletes"] = [
            ClientTuple(user=subject_key, relation=relation, object=object_key)
            for relation in to_del_relations
        ]
    if not payload:
        return
    return client.write(ClientWriteRequest(**payload))


def delete_all_subject_tuples(object_key: str):
    if not object_key:
        raise ValueError("object_key is required")

    existing_tuples = client.read(ReadRequestTupleKey(object=object_key)).tuples
    to_delete = [
        ClientTuple(user=t.key.user, relation=t.key.relation, object=t.key.object)
        for t in existing_tuples
    ]
    if to_delete:
        return client.write(ClientWriteRequest(deletes=to_delete))


def delete_all_object_tuples(subject_key: str, object_type: str):
    if not subject_key or not object_type:
        raise ValueError("subject_key and object_type are required")

    existing_tuples = client.read(
        ReadRequestTupleKey(
            user=subject_key,
            object=f"{object_type}:",
        )
    ).tuples
    to_delete = [
        ClientTuple(user=t.key.user, relation=t.key.relation, object=t.key.object)
        for t in existing_tuples
    ]
    if to_delete:
        return client.write(ClientWriteRequest(deletes=to_delete))
