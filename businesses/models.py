from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()


class Business(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='businesses')
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, help_text="آدرس یکتای منو")
    tagline = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    location_link = models.URLField(blank=True, help_text="لینک نقشه (Google Maps یا Neshan)")
    contact_email = models.EmailField(blank=True)
    primary_phone = models.CharField(max_length=50, blank=True)
    secondary_phone = models.CharField(max_length=50, blank=True)
    whatsapp = models.CharField(max_length=50, blank=True)
    telegram = models.CharField(max_length=100, blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='businesses/logos/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='businesses/covers/', blank=True, null=True)
    theme_primary = models.CharField(max_length=7, default="#4CAF50", help_text="کد رنگ اصلی #RRGGBB")
    theme_secondary = models.CharField(max_length=7, default="#263238", help_text="کد رنگ ثانویه #RRGGBB")
    show_hours = models.BooleanField(default=True, verbose_name="نمایش ساعات کاری", help_text="آیا ساعات کاری در منو نمایش داده شود؟")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = "کسب‌وکار"
        verbose_name_plural = "کسب‌وکارها"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            slug = base_slug
            counter = 1
            while Business.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('menu:business_detail', kwargs={'slug': self.slug})


class BusinessHour(models.Model):
    DAYS_OF_WEEK = [
        ('sat', 'شنبه'),
        ('sun', 'یکشنبه'),
        ('mon', 'دوشنبه'),
        ('tue', 'سه‌شنبه'),
        ('wed', 'چهارشنبه'),
        ('thu', 'پنجشنبه'),
        ('fri', 'جمعه'),
    ]

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='hours')
    day_of_week = models.CharField(max_length=3, choices=DAYS_OF_WEEK)
    opens_at = models.TimeField(blank=True, null=True)
    closes_at = models.TimeField(blank=True, null=True)
    is_closed = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=True, verbose_name="نمایش در منو", help_text="آیا این ساعت کاری در منو نمایش داده شود؟")

    class Meta:
        unique_together = ('business', 'day_of_week')
        ordering = ['business', 'day_of_week']
        verbose_name = "ساعت کاری"
        verbose_name_plural = "ساعات کاری"

    def __str__(self):
        day_display = dict(self.DAYS_OF_WEEK).get(self.day_of_week, self.day_of_week)
        if self.is_closed:
            return f"{self.business.name} - {day_display}: تعطیل"
        return f"{self.business.name} - {day_display}: {self.opens_at} تا {self.closes_at}"
