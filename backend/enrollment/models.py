from django.contrib.auth import get_user_model
from django.db import models

from courses.models import CourseClass

User = get_user_model()


class StudyGroup(models.Model):
    name = models.CharField(max_length=100)
    course_class = models.ForeignKey(
        "CourseClass", on_delete=models.CASCADE, related_name="study_groups"
    )
    description = models.TextField(blank=True, null=True)


class EnrollmentRole(models.IntegerChoices):
    TEACHER = 1, "Teacher"
    STUDENT = 2, "Student"
    GUEST = 3, "Guest"


class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    course_class = models.ForeignKey(
        CourseClass, on_delete=models.CASCADE, related_name="enrollments"
    )
    role = models.IntegerField(
        choices=EnrollmentRole.choices, default=EnrollmentRole.GUEST
    )
    study_group = models.ForeignKey(
        StudyGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enrollments",
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "course_class")  # one enrollment per user per class

    def __str__(self):
        return f"{self.user} - {self.course_class.name} ({self.get_role_display()})"
