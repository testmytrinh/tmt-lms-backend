from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import (
    Course,
    CourseCategory,
    CourseClass,
    CourseTemplate,
    Enrollment,
    Lesson,
    Module,
)

admin.site.register(CourseCategory, ModelAdmin)
admin.site.register(Course, ModelAdmin)
admin.site.register(CourseClass, ModelAdmin)
admin.site.register(Enrollment, ModelAdmin)
admin.site.register(CourseTemplate, ModelAdmin)
admin.site.register(Module, ModelAdmin)
admin.site.register(Lesson, ModelAdmin)
