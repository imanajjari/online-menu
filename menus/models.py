from datetime import datetime

from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from businesses.models import Business


class MenuCategory(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='categories')
    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=160)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='menus/categories/', blank=True, null=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('business', 'slug')
        ordering = ['order', 'title']
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

    def __str__(self):
        return f"{self.title} ({self.business.name})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title, allow_unicode=True)
            slug = base_slug
            counter = 1
            while MenuCategory.objects.filter(business=self.business, slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('menu:business_detail', kwargs={'slug': self.business.slug}) + f"#category-{self.slug}"


class MenuItem(models.Model):
    DAYS_OF_WEEK = [
        ('sat', 'شنبه'),
        ('sun', 'یکشنبه'),
        ('mon', 'دوشنبه'),
        ('tue', 'سه‌شنبه'),
        ('wed', 'چهارشنبه'),
        ('thu', 'پنجشنبه'),
        ('fri', 'جمعه'),
    ]

    category = models.ForeignKey(MenuCategory, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, blank=True)
    description = models.TextField(blank=True)
    price = models.PositiveIntegerField(help_text="قیمت به تومان")
    discount_percent = models.PositiveIntegerField(blank=True, null=True, help_text="تخفیف درصدی")
    special_price = models.PositiveIntegerField(blank=True, null=True, help_text="قیمت بعد از تخفیف (در صورت ثابت)")
    badge = models.CharField(max_length=50, blank=True, help_text="مانند جدید، ویژه")
    tags = models.CharField(max_length=200, blank=True, help_text="با کاما جدا کنید")
    ingredients = models.TextField(blank=True)
    calories = models.PositiveIntegerField(blank=True, null=True)
    primary_image = models.ImageField(upload_to='menus/items/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_full_time = models.BooleanField(default=True)
    available_days = models.CharField(max_length=120, blank=True, help_text="لیست روزها مثلا sat,sun")
    available_from = models.TimeField(blank=True, null=True)
    available_to = models.TimeField(blank=True, null=True)
    display_start = models.DateField(blank=True, null=True)
    display_end = models.DateField(blank=True, null=True)
    sort_order = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['sort_order', 'name']
        verbose_name = "آیتم منو"
        verbose_name_plural = "آیتم‌های منو"

    def __str__(self):
        return f"{self.name} ({self.category.business.name})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            slug = base_slug
            counter = 1
            while MenuItem.objects.filter(category__business=self.category.business, slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('menu:item_detail', kwargs={'business_slug': self.category.business.slug, 'item_slug': self.slug})

    def get_available_days_display(self):
        if self.is_full_time:
            return "همه روزها"
        mapping = dict(self.DAYS_OF_WEEK)
        return "، ".join(mapping.get(day, day) for day in self.available_days.split(',') if day)

    def is_visible(self, current_time=None):
        if not self.is_active:
            return False

        now = current_time or timezone.localtime()

        if self.display_start and now.date() < self.display_start:
            return False
        if self.display_end and now.date() > self.display_end:
            return False

        if self.is_full_time:
            return True

        day_code = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'][now.weekday()]
        allowed_days = [day.strip() for day in self.available_days.split(',') if day.strip()]
        if allowed_days and day_code not in allowed_days:
            return False

        if self.available_from and self.available_to:
            current_time_value = now.time()
            return self.available_from <= current_time_value <= self.available_to

        return True


class MenuItemImage(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to='menus/items/gallery/')
    caption = models.CharField(max_length=150, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصول"

    def __str__(self):
        return f"تصویر {self.menu_item.name}"
