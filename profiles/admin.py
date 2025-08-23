# profiles/admin.py
from django.contrib import admin
from profiles.models import ContactSubmission, Profile
from django.utils import timezone
from profiles.admin_filters import (
    RegistrationDateFilter,
    LastLoginFilter,
    ActivityLevelFilter,
)
from datetime import timedelta
from django.contrib.admin import SimpleListFilter, DateFieldListFilter
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count

User = get_user_model()

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


# ---------- Filters that work on the User queryset ----------


class UserRegistrationDateFilter(SimpleListFilter):
    title = "Registration Date"
    parameter_name = "registration_date"

    def lookups(self, request, model_admin):
        return (
            ("last_week", "Last 7 days"),
            ("last_month", "Last 30 days"),
            ("1_3_months", "1–3 months"),
            ("3_6_months", "3–6 months"),
            ("6_12_months", "6–12 months"),
            ("over_year", "Over a year"),
        )

    def queryset(self, request, qs):
        now = timezone.now()
        v = self.value()
        if v == "last_week":
            return qs.filter(date_joined__gte=now - timedelta(days=7))
        if v == "last_month":
            return qs.filter(date_joined__gte=now - timedelta(days=30))
        if v == "1_3_months":
            return qs.filter(
                date_joined__gte=now - timedelta(days=90),
                date_joined__lt=now - timedelta(days=30),
            )
        if v == "3_6_months":
            return qs.filter(
                date_joined__gte=now - timedelta(days=180),
                date_joined__lt=now - timedelta(days=90),
            )
        if v == "6_12_months":
            return qs.filter(
                date_joined__gte=now - timedelta(days=365),
                date_joined__lt=now - timedelta(days=180),
            )
        if v == "over_year":
            return qs.filter(date_joined__lt=now - timedelta(days=365))
        return qs


class UserLastLoginFilter(SimpleListFilter):
    title = "Last Login"
    parameter_name = "last_login"

    def lookups(self, request, model_admin):
        return (
            ("never", "Never logged in"),
            ("week", "This week"),
            ("month", "This month"),
            ("three_months", "1–3 months ago"),
            ("inactive", "Inactive >3 months"),
        )

    def queryset(self, request, qs):
        now = timezone.now()
        v = self.value()
        if v == "never":
            return qs.filter(last_login__isnull=True)
        if v == "week":
            return qs.filter(last_login__gte=now - timedelta(days=7))
        if v == "month":
            return qs.filter(last_login__gte=now - timedelta(days=30))
        if v == "three_months":
            return qs.filter(
                last_login__gte=now - timedelta(days=90),
                last_login__lt=now - timedelta(days=30),
            )
        if v == "inactive":
            return qs.filter(last_login__lt=now - timedelta(days=90))
        return qs


class UserActivityLevelFilter(SimpleListFilter):
    """
    Activity based on related Profile (reverse relation from User):
    profile__watched_videos and profile__enrolled_courses
    """

    title = "Activity Level"
    parameter_name = "activity_level"

    def lookups(self, request, model_admin):
        return (
            ("no_activity", "No Activity"),
            ("low", "Low (1–2 videos)"),
            ("medium", "Medium (3–10 videos)"),
            ("high", "High (>10 videos)"),
        )

    def queryset(self, request, qs):
        v = self.value()
        # annotate counts via the reverse relation to Profile
        qs = qs.annotate(_video_count=Count("profile__watched_videos", distinct=True))
        if v == "no_activity":
            return qs.filter(_video_count=0)
        if v == "low":
            return qs.filter(_video_count__gte=1, _video_count__lte=2)
        if v == "medium":
            return qs.filter(_video_count__gte=3, _video_count__lte=10)
        if v == "high":
            return qs.filter(_video_count__gt=10)
        return qs


class CustomUserAdmin(BaseUserAdmin):
    # columns
    list_display = BaseUserAdmin.list_display + (
        "date_joined",
        "last_login",
    )
    # filters (use our User-* versions, plus the built-in date widget)
    list_filter = BaseUserAdmin.list_filter + (
        ("date_joined", DateFieldListFilter),
        UserRegistrationDateFilter,
        UserLastLoginFilter,
        UserActivityLevelFilter,
    )
    date_hierarchy = "date_joined"


# replace stock admin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
