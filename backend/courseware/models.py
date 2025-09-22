from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.forms import ValidationError

from courses.models import CourseClass

User = get_user_model()


ALLOWED_CONTENT_TYPES = [
    "module",
    "lesson",
]
MAX_DEPTH = 3  # e.g., CourseTemplate -> Module -> Lesson


class ContentNode(models.Model):
    title = models.CharField(max_length=200)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    course_class = models.ForeignKey(
        CourseClass, on_delete=models.CASCADE, related_name="content_nodes"
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = [
            ("course_class", "parent", "order"),
            ("content_type", "object_id"),
        ]
        ordering = ["order"]

    def clean(self):
        if self.content_type.model not in ALLOWED_CONTENT_TYPES:
            raise ValidationError(f"Content type {self.content_type} is not allowed.")

        if self.parent and self.parent.course_class_id != self.course_class_id:
            raise ValidationError("Parent node must belong to the same course class.")

        if self.parent and self.parent.content_type.model != "module":
            raise ValidationError("Parent node must be of type 'module' or None.")

        # Depth check
        depth = 0
        parent = self.parent
        while parent:
            depth += 1
            parent = parent.parent
            if depth > MAX_DEPTH:
                raise ValidationError(f"Exceeded maximum depth of {MAX_DEPTH}.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        content_obj_id = self.content_object.id if self.content_object else "None"
        return (
            f"[class:{self.course_class_id}]"
            f"[{self.parent.title if self.parent else ''}] "
            f"({self.content_type.model}-<{self.content_object}>-{content_obj_id})"
        )


class Module(models.Model):
    content = models.TextField(blank=True)


class Lesson(models.Model):
    content = models.TextField(blank=True)


class CodingQuestion(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)
    hidden = models.BooleanField(default=False)
    returnable_forced = models.BooleanField(default=False)
    checksum = models.CharField(max_length=255, blank=True)
    has_tests = models.BooleanField(default=False)
    runtime_params = models.CharField(max_length=500, blank=True)
    code_review_requests_enabled = models.BooleanField(default=False)
    soft_deadline_spec = models.TextField(blank=True)
    hide_submission_results = models.BooleanField(default=False)
    memory_limit_gb = models.IntegerField(null=True, blank=True)
    cpu_limit = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name


class TestCase(models.Model):
    coding_question = models.ForeignKey(
        CodingQuestion, on_delete=models.CASCADE, related_name="test_cases"
    )
    input_data = models.TextField()
    expected_output = models.TextField()
    is_hidden = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    timeout = models.FloatField(default=2.0)  # seconds


class SupportedLanguage(models.Model):
    name = models.CharField(max_length=50)
    version = models.CharField(max_length=50, blank=True, null=True)


class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    coding_question = models.ForeignKey(CodingQuestion, on_delete=models.CASCADE)
    language = models.ForeignKey(SupportedLanguage, on_delete=models.CASCADE)
    code = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("running", "Running"),
            ("accepted", "Accepted"),
            ("wrong_answer", "Wrong Answer"),
            ("time_limit", "Time Limit Exceeded"),
            ("runtime_error", "Runtime Error"),
        ],
        default="pending",
    )
    result = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
