from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import File, Folder

admin.site.register(File, ModelAdmin)
admin.site.register(Folder, ModelAdmin)
