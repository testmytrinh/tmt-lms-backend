from django.contrib.auth import get_user_model
from django.db import models

from institution.models import Department, Term

User = get_user_model()


class CourseCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Course Categories"

    def __str__(self):
        return f"{self.name}"


class Course(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    categories = models.ManyToManyField(
        CourseCategory, blank=True, related_name="courses"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"


class CourseClass(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_open = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="classes")
    term = models.ForeignKey(
        Term,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="course_classes",
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="course_classes",
    )

    class Meta:
        verbose_name_plural = "Course Classes"

    def __str__(self):
        return f"[{self.pk}] {self.name} - {self.course.name}"
