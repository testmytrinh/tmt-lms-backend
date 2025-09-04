from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Config

admin.site.register(Config, ModelAdmin)
