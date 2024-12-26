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
            # Clean paths before saving
            obj.clean()
            super().save_model(request, obj, form, change)
            messages.success(
                request,
                'Successfully created redirect: "{}" to "{}"'.format(
                    obj.old_path.strip("/"), obj.new_path.strip("/")
                ),
            )
        except Exception as e:
            messages.error(request, f"Error saving redirect: {str(e)}")
            raise  # Re-raise the exception to trigger proper error handling

    def get_changeform_initial_data(self, request):
        return {"is_active": True}
