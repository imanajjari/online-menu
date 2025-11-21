from django.contrib import admin

from .models import Business, BusinessHour


class BusinessHourInline(admin.TabularInline):
    model = BusinessHour
    extra = 0


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "city", "primary_phone")
    search_fields = ("name", "owner__username", "city")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [BusinessHourInline]


@admin.register(BusinessHour)
class BusinessHourAdmin(admin.ModelAdmin):
    list_display = ("business", "day_of_week", "opens_at", "closes_at", "is_closed")
    list_filter = ("business", "day_of_week", "is_closed")
