from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import CourseTemplate, TemplateNode, Module, Lesson

# from .forms import TemplateNodeForm


class TemplateNodeAdmin(ModelAdmin):
    list_filter = ("course_template", "content_type")
    ordering = ("course_template", "parent", "order")
    # form = TemplateNodeForm


# Register your models here.
admin.site.register(CourseTemplate, ModelAdmin)
admin.site.register(Module, ModelAdmin)
admin.site.register(Lesson, ModelAdmin)
admin.site.register(TemplateNode, TemplateNodeAdmin)
