from django.forms.widgets import ClearableFileInput


class ImageFileInput(ClearableFileInput):
    accept = "image/png,image/jpeg,image/webp"
