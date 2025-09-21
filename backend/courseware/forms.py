from django import forms
from .models import ContentNode, ALLOWED_CONTENT_TYPES


class ContentNodeForm(forms.ModelForm):
    class Meta:
        model = ContentNode
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["content_type"].choices = [(ct, ct) for ct in ALLOWED_CONTENT_TYPES]
