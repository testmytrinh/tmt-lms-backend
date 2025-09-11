from django.contrib import admin
from unfold.admin import ModelAdmin

from enrollment.models import EnrollmentRole

from .models import Course, CourseCategory, CourseClass


class CourseClassAdmin(ModelAdmin):
    list_filter = ("is_active", "is_open", "term", "department", "course")
    search_fields = ("name", "description")
    list_display = (
        "id",
        "name",
        "course",
        "department",
        "is_open",
        "is_active",
        "start_date",
        "end_date",
        "term",
    )
    ordering = ("-start_date", "name")
    # list_sections = [CustomTableSection]

    @admin.display(description="Teachers (FGA)")
    def fga_teachers(self, obj: CourseClass):
        return obj.enrollments.filter(role=EnrollmentRole.TEACHER).count()

    @admin.display(description="Students (FGA)")
    def fga_students(self, obj: CourseClass):
        return obj.enrollments.filter(role=EnrollmentRole.STUDENT).count()

    @admin.display(description="Guests (FGA)")
    def fga_guests(self, obj: CourseClass):
        return obj.enrollments.filter(role=EnrollmentRole.GUEST).count()

    readonly_fields = ("fga_teachers", "fga_students", "fga_guests")

    fieldsets = (
        (None, {
            "fields": (
                "name", "description", "course", "term", "department", "course_template",
                "is_open", "is_active", "start_date", "end_date",
            )
        }),
        ("Enrollment stats", {
            "fields": ("fga_teachers", "fga_students", "fga_guests"),
        })
    )

admin.site.register(CourseCategory, ModelAdmin)
admin.site.register(Course, ModelAdmin)
admin.site.register(CourseClass, CourseClassAdmin)
