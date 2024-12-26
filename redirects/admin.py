from django.contrib import admin
from django.contrib import messages
from django.forms import ValidationError
from .models import URLRedirect


@admin.register(URLRedirect)
class URLRedirectAdmin(admin.ModelAdmin):
    list_display = ["old_path", "new_path", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["old_path", "new_path"]
    list_editable = ["is_active"]

    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
            messages.success(
                request,
                f'Successfully created redirect from "{obj.old_path}" to "{obj.new_path}"',
            )
        except ValidationError as e:
            for field, errors in e.message_dict.items():
                for error in errors:
                    messages.error(request, error)
