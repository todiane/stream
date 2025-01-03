# profiles/admin_filters.py

from django.contrib.admin import SimpleListFilter
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Q


class RegistrationDateFilter(SimpleListFilter):
    title = "Registration Date"
    parameter_name = "registration_date"

    def lookups(self, request, model_admin):
        return (
            ("last_week", "Last 7 days"),
            ("last_month", "Last 30 days"),
            ("1_3_months", "1-3 months"),
            ("3_6_months", "3-6 months"),
            ("6_12_months", "6-12 months"),
            ("over_year", "Over a year"),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == "last_week":
            return queryset.filter(user__date_joined__gte=now - timedelta(days=7))
        if self.value() == "last_month":
            return queryset.filter(user__date_joined__gte=now - timedelta(days=30))
        if self.value() == "1_3_months":
            return queryset.filter(
                user__date_joined__gte=now - timedelta(days=90),
                user__date_joined__lt=now - timedelta(days=30),
            )
        if self.value() == "3_6_months":
            return queryset.filter(
                user__date_joined__gte=now - timedelta(days=180),
                user__date_joined__lt=now - timedelta(days=90),
            )
        if self.value() == "6_12_months":
            return queryset.filter(
                user__date_joined__gte=now - timedelta(days=365),
                user__date_joined__lt=now - timedelta(days=180),
            )
        if self.value() == "over_year":
            return queryset.filter(user__date_joined__lt=now - timedelta(days=365))


class LastLoginFilter(SimpleListFilter):
    title = "Last Login"
    parameter_name = "last_login"

    def lookups(self, request, model_admin):
        return (
            ("never", "Never logged in"),
            ("week", "This week"),
            ("month", "This month"),
            ("three_months", "1-3 months ago"),
            ("inactive", "Inactive >3 months"),
        )

    def queryset(self, request, queryset):
        now = timezone.now()
        if self.value() == "never":
            return queryset.filter(user__last_login__isnull=True)
        if self.value() == "week":
            return queryset.filter(user__last_login__gte=now - timedelta(days=7))
        if self.value() == "month":
            return queryset.filter(user__last_login__gte=now - timedelta(days=30))
        if self.value() == "three_months":
            return queryset.filter(
                user__last_login__gte=now - timedelta(days=90),
                user__last_login__lt=now - timedelta(days=30),
            )
        if self.value() == "inactive":
            return queryset.filter(user__last_login__lt=now - timedelta(days=90))


class ActivityLevelFilter(SimpleListFilter):
    title = "Activity Level"
    parameter_name = "activity_level"

    def lookups(self, request, model_admin):
        return (
            ("no_activity", "No Activity"),
            ("low", "Low (1-2 videos)"),
            ("medium", "Medium (3-10 videos)"),
            ("high", "High (>10 videos)"),
        )

    def queryset(self, request, queryset):
        if self.value() == "no_activity":
            return queryset.annotate(video_count=Count("watched_videos")).filter(
                video_count=0
            )
        if self.value() == "low":
            return queryset.annotate(video_count=Count("watched_videos")).filter(
                video_count__gte=1, video_count__lte=2
            )
        if self.value() == "medium":
            return queryset.annotate(video_count=Count("watched_videos")).filter(
                video_count__gte=3, video_count__lte=10
            )
        if self.value() == "high":
            return queryset.annotate(video_count=Count("watched_videos")).filter(
                video_count__gt=10
            )
