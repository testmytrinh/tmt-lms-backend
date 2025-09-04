from django.contrib import admin
from unfold.admin import ModelAdmin

from .models import Department, Term

admin.site.register(Department, ModelAdmin)
admin.site.register(Term, ModelAdmin)
