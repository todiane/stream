# shop/forms.py
from django import forms
from .models import ProductReview


class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.RadioSelect(attrs={"class": "hidden peer"}),
            "comment": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "rows": 4,
                    "placeholder": "Share your thoughts about this product...",
                }
            ),
        }
