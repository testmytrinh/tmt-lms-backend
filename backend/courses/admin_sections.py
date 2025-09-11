from unfold.admin import ModelAdmin
from unfold.sections import TableSection, TemplateSection

from enrollment.models import EnrollmentRole

from .models import CourseClass

# Table for related records
class CustomTableSection(TableSection):
    pass

# Simple template with custom content
class CardSection(TemplateSection):
    template_name = "your_app/some_template.html"