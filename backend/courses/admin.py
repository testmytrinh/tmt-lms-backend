from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Course, CourseCategory, CourseClass


admin.site.register(CourseCategory, ModelAdmin)
admin.site.register(Course, ModelAdmin)
admin.site.register(CourseClass, ModelAdmin)
