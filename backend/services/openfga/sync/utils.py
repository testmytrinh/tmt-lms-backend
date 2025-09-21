from functools import partial
from openfga_sdk import ReadRequestTupleKey, Tuple
from openfga_sdk.client.models import (
    ClientListRelationsRequest,
    ClientListObjectsRequest,
    ClientWriteRequest,
    ClientTuple,
)

from . import client


def sync_single_type_subjects(
    object_key, subject_type, relation, desired_subject_ids: set[int]
):
    # Note: the result might contain subjects of other types
    existing_subject_tuples: list[Tuple] = client.read(
        ReadRequestTupleKey(
            object=object_key,
            relation=relation,
        )
    ).tuples
    # Filter only subjects of the correct type
    subject_prefix = f"{subject_type}:"
    existing_subject_ids: set[int] = set(
        int(t.key.user.removeprefix(subject_prefix))
        for t in existing_subject_tuples
        if t.key.user.startswith(subject_prefix)
    )

    to_add_subject_ids = desired_subject_ids - existing_subject_ids
    to_del_subject_ids = existing_subject_ids - desired_subject_ids

    make_tuple = partial(ClientTuple, relation=relation, object=object_key)

    payload = {}
    if to_add_subject_ids:
        payload["writes"] = [
            make_tuple(user=f"{subject_type}:{id}") for id in to_add_subject_ids
        ]
    if to_del_subject_ids:
        payload["deletes"] = [
            make_tuple(user=f"{subject_type}:{id}") for id in to_del_subject_ids
        ]

    if not payload:
        return
    return client.write(ClientWriteRequest(**payload))


def sync_single_type_objects(
    subject_key, object_type, relation, desired_object_ids: set[int]
):
    # Note: the result might contain objects of other types
    existing_object_tuples: list[Tuple] = client.read(
        ReadRequestTupleKey(
            user=subject_key,
            relation=relation,
            object=f"{object_type}:",
        )
    ).tuples
    # Filter only objects of the correct type
    object_prefix = f"{object_type}:"
    existing_object_ids: set[int] = set(
        int(t.key.object.removeprefix(object_prefix))
        for t in existing_object_tuples
        if t.key.object.startswith(object_prefix)
    )

    to_add_object_ids = desired_object_ids - existing_object_ids
    to_del_object_ids = existing_object_ids - desired_object_ids

    make_tuple = partial(ClientTuple, user=subject_key, relation=relation)

    payload = {}
    if to_add_object_ids:
        payload["writes"] = [
            make_tuple(object=f"{object_type}:{id}") for id in to_add_object_ids
        ]
    if to_del_object_ids:
        payload["deletes"] = [
            make_tuple(object=f"{object_type}:{id}") for id in to_del_object_ids
        ]

    if not payload:
        return
    return client.write(ClientWriteRequest(**payload))


def sync_relations(subject_key, object_key, desired_relations: set[str]):
    existing_tuples: list[Tuple] = client.read(
        ReadRequestTupleKey(
            user=subject_key,
            object=object_key,
        )
    ).tuples
    existing_relations: set[str] = set(t.key.relation for t in existing_tuples)

    to_add_relations = desired_relations - existing_relations
    to_del_relations = existing_relations - desired_relations

    make_tuple = partial(ClientTuple, user=subject_key, object=object_key)

    payload = {}
    if to_add_relations:
        payload["writes"] = [
            make_tuple(relation=relation) for relation in to_add_relations
        ]
    if to_del_relations:
        payload["deletes"] = [
            make_tuple(relation=relation) for relation in to_del_relations
        ]

    if not payload:
        return
    return client.write(ClientWriteRequest(**payload))


def delete_all_subject_tuples(object_key: str):
    existing_tuples = client.read(ReadRequestTupleKey(object=object_key)).tuples
    to_delete = [
        ClientTuple(user=t.key.user, relation=t.key.relation, object=t.key.object)
        for t in existing_tuples
    ]
    if to_delete:
        return client.write(ClientWriteRequest(deletes=to_delete))


def delete_all_object_tuples(subject_key: str, object_type: str):
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


def filter_allowed_relations(
    subject_key: str, object_key: str, relations: list[str]
) -> list[str]:
    if not subject_key or not object_key or not relations:
        raise ValueError("subject_key, object_key and relations are required")

    body = ClientListRelationsRequest(
        user=subject_key, object=object_key, relations=relations
    )
    return client.list_relations(body)
