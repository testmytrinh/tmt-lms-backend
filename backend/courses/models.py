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
    course_template = models.ForeignKey(
        "CourseTemplate",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="course_classes",
    )

    class Meta:
        verbose_name_plural = "Course Classes"

    def __str__(self):
        return f"{self.name} - {self.course.name}"


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


class Module(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    course_template = models.ForeignKey(
        CourseTemplate, on_delete=models.CASCADE, related_name="modules"
    )
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ("course_template", "order")
        ordering = ["order"]

    def __str__(self):
        return f"{self.title} (Module {self.order} of {self.course_template.title})"


class Lesson(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="lessons")
    order = models.PositiveIntegerField()

    class Meta:
        unique_together = ("module", "order")
        ordering = ["order"]

    def __str__(self):
        return f"{self.title} (Lesson {self.order} of {self.module.title})"
