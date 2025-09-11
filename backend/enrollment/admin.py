from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Enrollment, StudyGroup

@admin.register(Enrollment)
class EnrollmentAdmin(ModelAdmin):
    list_display = ("id", "user", "course_class", "role", "study_group", "enrolled_at")
    list_filter = ("role", "course_class", "study_group")
    search_fields = ("user__username", "user__email", "course_class__name")
    ordering = ("-enrolled_at",)

@admin.register(StudyGroup)
class StudyGroupAdmin(ModelAdmin):
    list_display = ("id", "name", "course_class", "description")
    list_filter = ("course_class",)
    search_fields = ("name", "description")
    ordering = ("name",)
    