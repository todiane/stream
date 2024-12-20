from django import forms
from .utils import sanitize_text
from .models import Category


class SanitizedCharField(forms.CharField):
    def clean(self, value):
        value = super().clean(value)
        return sanitize_text(value)


class CategoryForm(forms.ModelForm):
    name = SanitizedCharField(max_length=100)
    description = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Category
        fields = ["name", "slug", "description", "exam_board"]

    def clean_description(self):
        description = self.cleaned_data.get("description")
        return sanitize_text(description) if description else description
