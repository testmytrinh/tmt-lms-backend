from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from uuid import uuid4

User = get_user_model()


class Folder(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="subdirs"
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("owner", "name"),
                condition=models.Q(parent__isnull=True),
                name="uniq_root_name_per_owner",
            ),
            models.UniqueConstraint(
                fields=("parent", "name"),
                condition=models.Q(parent__isnull=False),
                name="uniq_child_name_per_parent",
            ),
        ]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}/"


def generate_file_key(instance: "File", filename: str) -> str:
    return f"{uuid4().hex}.{filename.split('.')[-1]}"


class File(models.Model):
    folder = models.ForeignKey(
        Folder, on_delete=models.CASCADE, null=True, blank=True, related_name="files"
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=generate_file_key)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=("owner", "name"),
                condition=models.Q(folder__isnull=True),
                name="uniq_root_file_name_per_owner",
            ),
            models.UniqueConstraint(
                fields=("folder", "name"),
                condition=models.Q(folder__isnull=False),
                name="uniq_file_name_per_folder",
            ),
        ]

    def open(self):
        return self.file.storage.open(self.file.name)

    def __str__(self):
        return f"{self.name}"
