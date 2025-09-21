from django.contrib import admin
from unfold.admin import ModelAdmin


from .models import ContentNode, Module, Lesson


class ContentNodeAdmin(ModelAdmin):
    list_display = (
        "id",
        "course_class",
        "my_model",
        "object_id",
        "parent",
        "order",
    )
    ordering = ("course_class", "parent", "order")

    @admin.display(description="Model")
    def my_model(self, obj):
        return obj.content_type.model


# Register your models here.
admin.site.register(Module, ModelAdmin)
admin.site.register(Lesson, ModelAdmin)
admin.site.register(ContentNode, ContentNodeAdmin)
