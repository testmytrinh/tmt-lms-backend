from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from services.openfga.relations import FileRelation, FolderRelation, UserRelation
from services.openfga.sync.utils import (
    sync_single_type_subjects,
    delete_all_subject_tuples,
)

from .models import File, Folder


@receiver(post_save, sender=Folder)
def sync_folder_in_openfga(sender, instance: Folder, created, **kwargs):
    sync_single_type_subjects(
        object_key=f"{FolderRelation.TYPE}:{instance.id}",
        subject_type=UserRelation.TYPE,
        relation=FolderRelation.OWNER,
        desired_subject_ids=set([str(instance.owner.id)]),
    )
    sync_single_type_subjects(
        object_key=f"{FolderRelation.TYPE}:{instance.id}",
        subject_type=FolderRelation.TYPE,
        relation=FolderRelation.PARENT,
        desired_subject_ids=set([str(instance.parent.id)])
        if instance.parent
        else set(),
    )


@receiver(post_save, sender=File)
def sync_file_in_openfga(sender, instance: File, created, **kwargs):
    sync_single_type_subjects(
        object_key=f"{FileRelation.TYPE}:{instance.id}",
        subject_type=UserRelation.TYPE,
        relation=FileRelation.OWNER,
        desired_subject_ids=set([str(instance.owner.id)]),
    )
    sync_single_type_subjects(
        object_key=f"{FileRelation.TYPE}:{instance.id}",
        subject_type=FolderRelation.TYPE,
        relation=FileRelation.PARENT,
        desired_subject_ids=set([str(instance.folder.id)])
        if instance.folder
        else set(),
    )


@receiver(post_delete, sender=File)
def delete_file_after_file_deletion(sender, instance: File, **kwargs):
    if instance.file is not None:
        # Delete file from filesystem or from online storage (like AWS S3).
        # We need to use save=False to allow the normal deletion from the database
        # to happen uninterrupted.
        instance.file.delete(save=False)
        delete_all_subject_tuples(object_key=f"{FileRelation.TYPE}:{instance.id}")
