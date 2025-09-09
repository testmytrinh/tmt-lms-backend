from django import forms
from .models import TemplateNode, ALLOWED_CONTENT_TYPES


class TemplateNodeForm(forms.ModelForm):
    class Meta:
        model = TemplateNode
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content_type"].choices = [(ct, ct) for ct in ALLOWED_CONTENT_TYPES]
