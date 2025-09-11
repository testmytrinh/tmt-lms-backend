from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from unfold.admin import ModelAdmin

from openfga_sdk.client.models.list_users_request import ClientListUsersRequest
from openfga_sdk.client.models.list_objects_request import ClientListObjectsRequest
from openfga_sdk.models.fga_object import FgaObject

from proxies.openfga.sync import client as fga
from proxies.openfga.relations import CourseTemplateRelation, CourseClassRelation
from django.contrib.auth import get_user_model

from .models import CourseTemplate, TemplateNode, Module, Lesson

# from .forms import TemplateNodeForm


class TemplateNodeAdmin(ModelAdmin):
    list_display = (
        "id",
        "course_template",
        "my_model",
        "object_id",
        "parent",
        "order",
    )
    ordering = ("course_template", "parent", "order")

    @admin.display(description='Model')
    def my_model(self, obj):
        return obj.content_type.model


class CourseTemplateAdmin(ModelAdmin):
    list_display = ("id", "title", "owner", "created_at", "updated_at")


# Register your models here.
admin.site.register(CourseTemplate, CourseTemplateAdmin)
admin.site.register(Module, ModelAdmin)
admin.site.register(Lesson, ModelAdmin)
admin.site.register(TemplateNode, TemplateNodeAdmin)
