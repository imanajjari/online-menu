from django.contrib import admin

from .models import MenuCategory, MenuItem, MenuItemImage


class MenuItemImageInline(admin.TabularInline):
    model = MenuItemImage
    extra = 0


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "business", "order", "is_active")
    list_filter = ("business", "is_active")
    search_fields = ("title", "business__name")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_active", "is_featured")
    list_filter = ("category", "is_active", "is_featured")
    search_fields = ("name", "description", "category__title")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [MenuItemImageInline]


@admin.register(MenuItemImage)
class MenuItemImageAdmin(admin.ModelAdmin):
    list_display = ("menu_item", "order")
    list_filter = ("menu_item",)
