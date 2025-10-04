from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, transaction

from ..models import File, Folder

User = get_user_model()


class FileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com", password="pass123", is_active=True
        )

    def test_create_root_file(self):
        to_upload_file = SimpleUploadedFile("file1.txt", b"file_content")
        f = File.objects.create(owner=self.user, name="file1.txt", file=to_upload_file)
        self.assertIsNone(f.folder)
        self.assertEqual(f.owner, self.user)
        self.assertEqual(f.name, "file1.txt")
        self.assertIsNotNone(f.created_at)
        self.assertIsNotNone(f.updated_at)
        with f.open() as opened_file:
            self.assertEqual(opened_file.read(), b"file_content")

    def test_create_file_in_folder(self):
        folder = Folder.objects.create(name="folder1", owner=self.user)
        to_upload_file = SimpleUploadedFile("file2.txt", b"file_content")
        f = File.objects.create(
            folder=folder, owner=self.user, name="file2.txt", file=to_upload_file
        )
        self.assertEqual(f.folder, folder)
        self.assertEqual(f.owner, self.user)
        self.assertEqual(f.name, "file2.txt")
        self.assertIsNotNone(f.created_at)
        self.assertIsNotNone(f.updated_at)
        with f.open() as opened_file:
            self.assertEqual(opened_file.read(), b"file_content")
        self.assertIn(f, list(folder.files.all()))

    def test_unique_root_file_name_per_owner(self):
        to_upload_file1 = SimpleUploadedFile("file1.txt", b"file_content")
        File.objects.create(owner=self.user, name="file1.txt", file=to_upload_file1)
        to_upload_file2 = SimpleUploadedFile("file1.txt", b"file_content")
        with self.assertRaises(IntegrityError), transaction.atomic():
            File.objects.create(owner=self.user, name="file1.txt", file=to_upload_file2)

        other_user = User.objects.create_user(
            email="other_user@example.com", password="pass123", is_active=True
        )
        try:
            File.objects.create(
                owner=other_user, name="file1.txt", file=to_upload_file2
            )
        except Exception:
            self.fail(
                "Creating a file with the same name for a different user should not raise an exception."
            )

    def test_unique_file_name_per_folder(self):
        folder = Folder.objects.create(name="folder1", owner=self.user)
        to_upload_file1 = SimpleUploadedFile("file1.txt", b"file_content")
        File.objects.create(
            folder=folder, owner=self.user, name="file1.txt", file=to_upload_file1
        )
        to_upload_file2 = SimpleUploadedFile("file1.txt", b"file_content")
        with self.assertRaises(IntegrityError), transaction.atomic():
            File.objects.create(
                folder=folder, owner=self.user, name="file1.txt", file=to_upload_file2
            )

        other_user = User.objects.create_user(
            email="other_user@example.com", password="pass123", is_active=True
        )
        try:
            File.objects.create(
                owner=other_user, name="file1.txt", file=to_upload_file2
            )
        except Exception:
            self.fail(
                "Creating a file with the same name for a different user should not raise an exception."
            )


class FolderModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com", password="pass123", is_active=True
        )

    def test_create_root_folder(self):
        folder = Folder.objects.create(name="root_folder", owner=self.user)
        self.assertIsNone(folder.parent)
        self.assertEqual(folder.name, "root_folder")
        self.assertEqual(folder.owner, self.user)
        self.assertIsNotNone(folder.created_at)
        self.assertIsNotNone(folder.updated_at)

    def test_create_subfolder(self):
        parent_folder = Folder.objects.create(name="parent_folder", owner=self.user)
        subfolder = Folder.objects.create(
            name="sub_folder", parent=parent_folder, owner=self.user
        )
        self.assertEqual(subfolder.parent, parent_folder)
        self.assertEqual(subfolder.name, "sub_folder")
        self.assertEqual(subfolder.owner, self.user)
        self.assertIsNotNone(subfolder.created_at)
        self.assertIsNotNone(subfolder.updated_at)
        self.assertIn(subfolder, list(parent_folder.subdirs.all()))
        self.assertNotIn(parent_folder, list(subfolder.subdirs.all()))

    def test_unique_root_folder_name_per_owner(self):
        Folder.objects.create(name="unique_folder", owner=self.user)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Folder.objects.create(name="unique_folder", owner=self.user)

        other_user = User.objects.create_user(
            email="other_user@example.com", password="pass123", is_active=True
        )
        try:
            Folder.objects.create(name="unique_folder", owner=other_user)
        except Exception:
            self.fail(
                "Creating a folder with the same name for a different user should not raise an exception."
            )

    def test_unique_subfolder_name_per_parent(self):
        parent_folder = Folder.objects.create(name="parent_folder", owner=self.user)
        Folder.objects.create(
            name="unique_subfolder", parent=parent_folder, owner=self.user
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            Folder.objects.create(
                name="unique_subfolder", parent=parent_folder, owner=self.user
            )
        # Even with other owner, should still raise IntegrityError
        other_user = User.objects.create_user(
            email="other_user@example.com", password="pass123", is_active=True
        )
        with self.assertRaises(IntegrityError), transaction.atomic():
            Folder.objects.create(
                name="unique_subfolder", parent=parent_folder, owner=other_user
            )

    def test_cascade_delete(self):
        parent_folder = Folder.objects.create(name="parent_folder", owner=self.user)
        subfolder = Folder.objects.create(
            name="sub_folder", parent=parent_folder, owner=self.user
        )
        to_upload_file = SimpleUploadedFile("file_in_subfolder.txt", b"file_content")
        file_in_subfolder = File.objects.create(
            folder=subfolder,
            owner=self.user,
            name="file_in_subfolder.txt",
            file=to_upload_file,
        )
        to_upload_file_root = SimpleUploadedFile("file_in_root.txt", b"file_content")
        file_in_root = File.objects.create(
            owner=self.user, name="file_in_root.txt", file=to_upload_file_root
        )

        parent_folder.delete()

        self.assertFalse(Folder.objects.filter(id=parent_folder.id).exists())
        self.assertFalse(Folder.objects.filter(id=subfolder.id).exists())
        self.assertFalse(File.objects.filter(id=file_in_subfolder.id).exists())
        self.assertTrue(File.objects.filter(id=file_in_root.id).exists())
