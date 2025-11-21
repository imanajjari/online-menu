from django import forms
from django.forms import ClearableFileInput, inlineformset_factory

from .models import MenuCategory, MenuItem, MenuItemImage


class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True


class MenuCategoryForm(forms.ModelForm):
    class Meta:
        model = MenuCategory
        fields = ["title", "description", "cover_image", "is_active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # فارسی کردن label ها
        labels = {
            "title": "عنوان",
            "description": "توضیحات",
            "cover_image": "عکس کاور",
            "is_active": "فعال",
        }
        
        for name, field in self.fields.items():
            if name in labels:
                field.label = labels[name]
            classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"input-control {classes}".strip()
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("rows", 3)


class MenuItemForm(forms.ModelForm):
    available_days_list = forms.MultipleChoiceField(
        choices=MenuItem.DAYS_OF_WEEK,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="روزهای ارائه",
    )
    gallery_images = forms.FileField(
        required=False,
        widget=MultiFileInput(attrs={"multiple": True}),
        label="تصاویر گالری",
        help_text="می‌توانید چند تصویر انتخاب کنید",
    )

    class Meta:
        model = MenuItem
        fields = [
            "category",
            "name",
            "description",
            "price",
            "discount_percent",
            "special_price",
            "badge",
            "tags",
            "ingredients",
            "calories",
            "primary_image",
            "is_active",
            "is_featured",
            "is_full_time",
            "available_from",
            "available_to",
            "display_start",
            "display_end",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "ingredients": forms.Textarea(attrs={"rows": 3}),
            "tags": forms.TextInput(attrs={"placeholder": "قهوه، سرد"}),
            "available_from": forms.TimeInput(attrs={"type": "time"}),
            "available_to": forms.TimeInput(attrs={"type": "time"}),
            "display_start": forms.DateInput(attrs={"type": "text", "class": "persian-date-input"}),
            "display_end": forms.DateInput(attrs={"type": "text", "class": "persian-date-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get("instance") or getattr(self, "instance", None)
        if instance and instance.available_days:
            self.fields["available_days_list"].initial = [day for day in instance.available_days.split(',') if day]
        if instance is None:
            self.fields["is_full_time"].initial = True
        
        # فارسی کردن label ها
        labels = {
            "category": "دسته‌بندی",
            "name": "نام محصول",
            "description": "توضیحات",
            "price": "قیمت (تومان)",
            "discount_percent": "درصد تخفیف",
            "special_price": "قیمت ویژه",
            "badge": "نشان (بدج)",
            "tags": "برچسب‌ها",
            "ingredients": "مواد تشکیل‌دهنده",
            "calories": "کالری",
            "primary_image": "عکس اصلی",
            "is_active": "فعال",
            "is_featured": "ویژه",
            "is_full_time": "همه روزها (فول تایم)",
            "available_from": "ساعت شروع",
            "available_to": "ساعت پایان",
            "display_start": "تاریخ شروع نمایش",
            "display_end": "تاریخ پایان نمایش",
        }
        
        for name, field in self.fields.items():
            if name in labels:
                field.label = labels[name]
            if name in {"available_days_list", "gallery_images"}:
                field.widget.attrs.setdefault("class", "choice-list")
            else:
                classes = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = f"input-control {classes}".strip()
            if field.required:
                field.widget.attrs.setdefault("required", "required")

    def clean(self):
        cleaned_data = super().clean()
        is_full_time = cleaned_data.get("is_full_time")
        available_from = cleaned_data.get("available_from")
        available_to = cleaned_data.get("available_to")
        available_days = cleaned_data.get("available_days_list")

        if not is_full_time:
            if not available_days:
                self.add_error("available_days_list", "حداقل یک روز را انتخاب کنید.")
            if not available_from or not available_to:
                self.add_error("available_from", "ساعات شروع و پایان را مشخص کنید.")
            if available_from and available_to and available_from >= available_to:
                self.add_error("available_to", "ساعت پایان باید بعد از ساعت شروع باشد.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.is_full_time:
            instance.available_days = ""
            instance.available_from = None
            instance.available_to = None
        else:
            days = self.cleaned_data.get("available_days_list", [])
            instance.available_days = ",".join(days)
        if commit:
            instance.save()
            self.save_m2m()
        return instance


MenuItemImageFormSet = inlineformset_factory(
    MenuItem,
    MenuItemImage,
    fields=["image", "caption", "order"],
    extra=0,
    can_delete=True,
)

