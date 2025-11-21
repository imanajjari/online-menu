from django import forms
from django.forms import inlineformset_factory

from .models import Business, BusinessHour


class BusinessForm(forms.ModelForm):
    class Meta:
        model = Business
        fields = [
            "name",
            "slug",
            "tagline",
            "description",
            "address",
            "city",
            "location_link",
            "contact_email",
            "primary_phone",
            "secondary_phone",
            "whatsapp",
            "telegram",
            "instagram",
            "website",
            "logo",
            "cover_image",
            "theme_primary",
            "theme_secondary",
            "show_hours",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "address": forms.Textarea(attrs={"rows": 3}),
            "theme_primary": forms.TextInput(attrs={"type": "color"}),
            "theme_secondary": forms.TextInput(attrs={"type": "color"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # فارسی کردن label ها
        labels = {
            "name": "نام کسب‌وکار",
            "slug": "نشانی یکتا",
            "tagline": "شعار",
            "description": "توضیحات",
            "address": "آدرس",
            "city": "شهر",
            "location_link": "لینک موقعیت",
            "contact_email": "ایمیل تماس",
            "primary_phone": "تلفن اصلی",
            "secondary_phone": "تلفن ثانویه",
            "whatsapp": "واتساپ",
            "telegram": "تلگرام",
            "instagram": "اینستاگرام",
            "website": "وب‌سایت",
            "logo": "لوگو",
            "cover_image": "عکس کاور",
            "theme_primary": "رنگ اصلی",
            "theme_secondary": "رنگ ثانویه",
            "show_hours": "نمایش ساعات کاری",
        }
        
        for name, field in self.fields.items():
            if name in labels:
                field.label = labels[name]
            classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"input-control {classes}".strip()
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("rows", 3)
            if field.required:
                field.widget.attrs["required"] = "required"
        if "slug" in self.fields:
            self.fields["slug"].help_text = "نشانی یکتا برای منو (فقط حروف لاتین، عدد و -)"


BusinessHourFormSet = inlineformset_factory(
    Business,
    BusinessHour,
    fields=["day_of_week", "opens_at", "closes_at", "is_closed", "is_visible"],
    extra=0,
    can_delete=False,
)

