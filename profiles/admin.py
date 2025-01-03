# profiles/admin.py
from django.contrib import admin
from profiles.models import ContactSubmission, Profile
from django.utils import timezone
from .models import Profile
from profiles.admin_filters import (
    RegistrationDateFilter,
    LastLoginFilter,
    ActivityLevelFilter,
)

admin.site.site_header = "Stream English Administration"
admin.site.site_title = "Stream English Admin Portal"
admin.site.index_title = "Welcome to Stream English Admin Portal"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "first_name",
        "email_verified",
        "get_registration_date",
        "get_last_login",
        "get_video_count",
        "get_enrolled_courses_count",
    ]
    list_filter = [
        RegistrationDateFilter,
        LastLoginFilter,
        ActivityLevelFilter,
        "email_verified",
        "email_subscribed",
    ]
    search_fields = ["user__username", "user__email", "first_name"]
    filter_horizontal = ["enrolled_courses", "watched_videos"]
    raw_id_fields = ["user", "last_watched_lesson"]

    def get_registration_date(self, obj):
        return obj.user.date_joined.strftime("%Y-%m-%d")

    get_registration_date.short_description = "Registered"
    get_registration_date.admin_order_field = "user__date_joined"

    def get_last_login(self, obj):
        if obj.user.last_login:
            return obj.user.last_login.strftime("%Y-%m-%d")
        return "Never"

    get_last_login.short_description = "Last Login"
    get_last_login.admin_order_field = "user__last_login"

    def get_video_count(self, obj):
        return obj.watched_videos.count()

    get_video_count.short_description = "Videos Watched"

    def get_enrolled_courses_count(self, obj):
        return obj.enrolled_courses.count()

    get_enrolled_courses_count.short_description = "Enrolled Courses"

    fieldsets = (
        (None, {"fields": ("user", "first_name", "bio")}),
        (
            "Course Information",
            {"fields": ("enrolled_courses", "watched_videos", "last_watched_lesson")},
        ),
        (
            "Settings",
            {
                "fields": ("email_verified", "email_subscribed"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "reason",
        "created_at",
        "name",
        "parent_name",
        "parent_email",
    )
    list_filter = ("reason", "created_at")
    search_fields = (
        "user__username",
        "user__email",
        "description",
        "parent_first_name",
        "parent_last_name",
        "parent_email",
    )
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("user", "reason", "name", "description")}),
        (
            "Parent/Guardian Details",
            {
                "fields": (
                    "parent_first_name",
                    "parent_last_name",
                    "parent_email",
                    "parent_phone",
                ),
                "classes": ("collapse",),  # Makes this section collapsible
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def parent_name(self, obj):
        if obj.parent_first_name or obj.parent_last_name:
            return f"{obj.parent_first_name} {obj.parent_last_name}".strip()
        return "-"

    parent_name.short_description = "Parent Name"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user")
