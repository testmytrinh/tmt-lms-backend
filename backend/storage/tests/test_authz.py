from django.test import TestCase
from openfga_sdk.client.models import (
    ClientBatchCheckRequest,
    ClientBatchCheckItem,
)
from functools import partial

from services.openfga.sync import client as ofga
from services.openfga.relations import UserRelation, FileRelation, FolderRelation

from ..models import File, Folder
from django.contrib.auth import get_user_model

User = get_user_model()


class FileAuthzSyncTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="pass123", is_active=True
        )

    def test_file_creation_sync(self):
        f = File.objects.create(owner=self.user, name="file1.txt")

        make_check_item = partial(
            ClientBatchCheckItem,
            user=f"{UserRelation.TYPE}:{self.user.id}",
            object=f"{FileRelation.TYPE}:{f.id}",
        )

        res = ofga.batch_check(
            ClientBatchCheckRequest(
                checks=[
                    make_check_item(relation=FileRelation.OWNER),
                    make_check_item(relation=FileRelation.CAN_VIEW),
                    make_check_item(relation=FileRelation.CAN_EDIT),
                ]
            )
        ).result

        self.assertTrue(all(item.allowed for item in res))

    def test_file_in_folder_sync(self):
        folder = Folder.objects.create(name="folder1", owner=self.user)
        other_user = User.objects.create_user(
            email="otheruser@example.com", password="pass123", is_active=True
        )
        f = File.objects.create(folder=folder, owner=other_user, name="file2.txt")

        file_check = partial(
            ClientBatchCheckItem,
            object=f"{FileRelation.TYPE}:{f.id}",
        )

        res = ofga.batch_check(
            ClientBatchCheckRequest(
                checks=[
                    file_check(
                        user=f"{FolderRelation.TYPE}:{folder.id}",
                        relation=FileRelation.PARENT,
                    ),
                    file_check(
                        user=f"{UserRelation.TYPE}:{self.user.id}",
                        relation=FileRelation.CAN_VIEW,
                    ),
                    file_check(
                        user=f"{UserRelation.TYPE}:{self.user.id}",
                        relation=FileRelation.CAN_EDIT,
                    ),
                ]
            )
        ).result

        self.assertTrue(all(item.allowed for item in res))

    def test_file_deletion_sync(self):
        f = File.objects.create(owner=self.user, name="file1.txt")
        f_id = f.id
        f.delete()

        u_f_check = partial(
            ClientBatchCheckItem,
            user=f"{UserRelation.TYPE}:{self.user.id}",
            object=f"{FileRelation.TYPE}:{f_id}",
        )

        res = ofga.batch_check(
            ClientBatchCheckRequest(
                checks=[
                    u_f_check(relation=FileRelation.OWNER),
                    u_f_check(relation=FileRelation.CAN_VIEW),
                    u_f_check(relation=FileRelation.CAN_EDIT),
                ]
            )
        ).result

        self.assertTrue(all(not item.allowed for item in res))

    def test_file_move_sync(self):
        o_user = User.objects.create_user(
            email="otheruser@example.com", password="pass123", is_active=True
        )
        folder1 = Folder.objects.create(name="folder1", owner=self.user)
        folder2 = Folder.objects.create(name="folder2", owner=o_user)
        file = File.objects.create(folder=folder1, owner=self.user, name="file1.txt")

        files_parent_check = partial(
            ClientBatchCheckItem,
            relation=FileRelation.PARENT,
            object=f"{FileRelation.TYPE}:{file.id}",
        )
        view_check = partial(
            ClientBatchCheckItem,
            relation=FileRelation.CAN_VIEW,
            object=f"{FileRelation.TYPE}:{file.id}",
        )
        edit_check = partial(
            ClientBatchCheckItem,
            relation=FileRelation.CAN_EDIT,
            object=f"{FileRelation.TYPE}:{file.id}",
        )
        owner_check = partial(
            ClientBatchCheckItem,
            relation=FileRelation.OWNER,
            object=f"{FileRelation.TYPE}:{file.id}",
        )

        res = ofga.batch_check(
            ClientBatchCheckRequest(
                checks=[
                    files_parent_check(
                        user=f"{FolderRelation.TYPE}:{folder1.id}", correlation_id="1"
                    ),
                    files_parent_check(
                        user=f"{FolderRelation.TYPE}:{folder2.id}", correlation_id="2"
                    ),
                ]
            )
        ).result

        allowed_map = {item.correlation_id: item.allowed for item in res}
        self.assertTrue(allowed_map["1"])  # In folder1
        self.assertFalse(allowed_map["2"])  # Not in folder2

        file.folder = folder2
        file.save(update_fields=["folder"])
        res = ofga.batch_check(
            ClientBatchCheckRequest(
                checks=[
                    files_parent_check(
                        user=f"{FolderRelation.TYPE}:{folder1.id}", correlation_id="1"
                    ),
                    files_parent_check(
                        user=f"{FolderRelation.TYPE}:{folder2.id}", correlation_id="2"
                    ),
                    view_check(
                        user=f"{UserRelation.TYPE}:{self.user.id}", correlation_id="3"
                    ),
                    edit_check(
                        user=f"{UserRelation.TYPE}:{self.user.id}", correlation_id="4"
                    ),
                    owner_check(
                        user=f"{UserRelation.TYPE}:{self.user.id}", correlation_id="5"
                    ),
                    view_check(
                        user=f"{UserRelation.TYPE}:{o_user.id}", correlation_id="6"
                    ),
                    edit_check(
                        user=f"{UserRelation.TYPE}:{o_user.id}", correlation_id="7"
                    ),
                    owner_check(
                        user=f"{UserRelation.TYPE}:{o_user.id}", correlation_id="8"
                    ),
                ]
            )
        ).result
        allowed_map = {item.correlation_id: item.allowed for item in res}
        self.assertFalse(allowed_map["1"])  # No longer in folder1
        self.assertTrue(allowed_map["2"])  # Now in folder2
        self.assertTrue(allowed_map["3"])  # owner can view
        self.assertTrue(allowed_map["4"])  # owner can edit
        self.assertTrue(allowed_map["5"])  # owner is still the owner
        self.assertTrue(allowed_map["6"])  # Owner of new parent can view
        self.assertTrue(allowed_map["7"])  # Owner of new parent can edit
        self.assertFalse(allowed_map["8"])  # Owner of new parent is not the owner

class FolderAuthzSyncTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="folder_owner@example.com", password="pass123", is_active=True
        )
        self.other_user = User.objects.create_user(
            email="folder_member@example.com", password="pass123", is_active=True
        )
    
    def test_folder_creation_sync(self):
        folder = Folder.objects.create(name="my_folder", owner=self.user)

        make_check_item = partial(
            ClientBatchCheckItem,
            user=f"{UserRelation.TYPE}:{self.user.id}",
            object=f"{FolderRelation.TYPE}:{folder.id}",
        )

        res = ofga.batch_check(
            ClientBatchCheckRequest(
                checks=[
                    make_check_item(relation=FolderRelation.OWNER),
                    make_check_item(relation=FolderRelation.CAN_VIEW),
                    make_check_item(relation=FolderRelation.CAN_EDIT),
                ]
            )
        ).result

        self.assertTrue(all(item.allowed for item in res))