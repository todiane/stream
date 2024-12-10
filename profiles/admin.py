# profiles/admin.py
from django.contrib import admin
from profiles.models import ContactSubmission

admin.site.site_header = "Stream English Administration"
admin.site.site_title = "Stream English Admin Portal"
admin.site.index_title = "Welcome to Stream English Admin Portal"

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'reason', 'created_at', 'name', 'parent_name', 'parent_email')
    list_filter = ('reason', 'created_at')
    search_fields = ('user__username', 'user__email', 'description', 
                    'parent_first_name', 'parent_last_name', 'parent_email')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'reason', 'name', 'description')
        }),
        ('Parent/Guardian Details', {
            'fields': ('parent_first_name', 'parent_last_name', 'parent_email', 'parent_phone'),
            'classes': ('collapse',),  # Makes this section collapsible
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        })
    )

    def parent_name(self, obj):
        if obj.parent_first_name or obj.parent_last_name:
            return f"{obj.parent_first_name} {obj.parent_last_name}".strip()
        return "-"
    parent_name.short_description = "Parent Name"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')