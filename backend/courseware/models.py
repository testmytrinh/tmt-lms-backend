from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.forms import ValidationError

User = get_user_model()


class CourseTemplate(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="course_templates",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} (by {self.owner if self.owner else 'Unknown'})"


ALLOWED_CONTENT_TYPES = [
    "module",
    "lesson",
]
MAX_DEPTH = 3  # e.g., CourseTemplate -> Module -> Lesson


class TemplateNode(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    course_template = models.ForeignKey(
        CourseTemplate, on_delete=models.CASCADE, related_name="template_nodes"
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = [
            ("course_template", "parent", "order"),
            ("content_type", "object_id"),
        ]
        ordering = ["order"]

    def clean(self):
        if self.content_type.model not in ALLOWED_CONTENT_TYPES:
            raise ValidationError(f"Content type {self.content_type} is not allowed.")

        if self.parent and self.parent.course_template != self.course_template:
            raise ValidationError(
                "Parent node must belong to the same course template."
            )

        # Depth check
        depth = 0
        parent = self.parent
        while parent:
            depth += 1
            parent = parent.parent
        if depth > MAX_DEPTH:
            raise ValidationError(f"Exceeded maximum depth of {MAX_DEPTH}.")

    def __str__(self):
        content_obj_id = self.content_object.id if self.content_object else "None"
        return f"[{self.course_template.title}({self.course_template.id})][{self.parent.content_object.title if self.parent else ''}] ({self.content_type.model}-<{self.content_object}>-{content_obj_id})"


class Module(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title}"


class Lesson(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title}"
