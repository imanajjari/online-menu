from io import BytesIO
from pathlib import Path
from datetime import time

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile

from businesses.models import Business, BusinessHour
from menus.models import MenuCategory, MenuItem, MenuItemImage

COLORS = {
    "logo": (63, 81, 181),
    "cover": (55, 71, 79),
    "espresso": (198, 93, 72),
    "latte": (154, 118, 91),
    "cheesecake": (237, 187, 153),
}


def make_image(color, text, size=(800, 500)):
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGB", size, color)
    draw = ImageDraw.Draw(img)
    font_size = int(min(size) / 8)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:  # noqa: BLE001
        font = ImageFont.load_default()
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2)
    draw.text(position, text, fill="white", font=font)
    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=90)
    return ContentFile(buffer.getvalue())


def assign_business_hours(business):
    schedule = {
        "sat": ("08:00", "23:00"),
        "sun": ("08:00", "23:00"),
        "mon": ("08:00", "23:00"),
        "tue": ("08:00", "23:00"),
        "wed": ("08:00", "23:00"),
        "thu": ("08:00", "23:59"),
        "fri": (None, None),
    }

    for day, (opens, closes) in schedule.items():
        hour, __created = BusinessHour.objects.get_or_create(
            business=business,
            day_of_week=day,
        )
        if opens and closes:
            hour.opens_at = opens
            hour.closes_at = closes
            hour.is_closed = False
        else:
            hour.opens_at = None
            hour.closes_at = None
            hour.is_closed = True
        hour.save()


def create_demo_business():
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username="demo_owner",
        defaults={
            "first_name": "ایمان",
            "last_name": "نجاری",
            "email": "owner@example.com",
        },
    )
    if created:
        user.set_password("demo1234")
        user.save()

    business, _ = Business.objects.get_or_create(
        owner=user,
        slug="کافه-ایمان-نجاری",
        defaults={"name": "کافه ایمان نجاری"},
    )

    business.name = "کافه ایمان نجاری"
    business.tagline = "اسپرسو بار مدرن با دسرهای دست‌ساز"
    business.description = "کافه‌ای دنج در قلب شهر با تمرکز بر قهوه‌های تخصصی، نوشیدنی‌های فصل و دسرهای خانگی."
    business.address = "تهران، خیابان ولیعصر، بالاتر از پارک ملت، پلاک ۲۳۱"
    business.city = "تهران"
    business.location_link = "https://maps.google.com/?q=35.771,51.412"
    business.contact_email = "info@iman-cafe.ir"
    business.primary_phone = "021-12345678"
    business.secondary_phone = "0912-123-4567"
    business.instagram = "iman_cafe"
    business.telegram = "imancafe"
    business.whatsapp = "09121234567"
    business.theme_primary = "#5A3F37"
    business.theme_secondary = "#2F2519"

    # Assign visuals
    if not business.logo:
        business.logo.save(
            "iman_cafe_logo.jpg",
            make_image(COLORS["logo"], "کافه ایمان"),
            save=False,
        )
    if not business.cover_image:
        business.cover_image.save(
            "iman_cafe_cover.jpg",
            make_image(COLORS["cover"], "Café Iman"),
            save=False,
        )
    business.save()

    assign_business_hours(business)

    desired_category_slugs = ["hot-drinks", "desserts"]

    hot_drinks, _ = MenuCategory.objects.update_or_create(
        business=business,
        slug="hot-drinks",
        defaults={
            "title": "نوشیدنی‌های گرم",
            "description": "قهوه‌های اسپشیالتی و نوشیدنی‌های فصلی گرم.",
            "order": 1,
            "is_active": True,
        },
    )

    desserts, _ = MenuCategory.objects.update_or_create(
        business=business,
        slug="desserts",
        defaults={
            "title": "دسرهای خانگی",
            "description": "شیرینی‌ها و دسرهای تازه روز.",
            "order": 2,
            "is_active": True,
        },
    )

    # Remove old categories not in desired list
    business.categories.exclude(slug__in=desired_category_slugs).delete()

    desired_item_slugs = [
        "espresso-double-shot",
        "caramel-latte",
        "raspberry-cheesecake",
    ]

    espresso, _ = MenuItem.objects.update_or_create(
        category=hot_drinks,
        slug="espresso-double-shot",
        defaults={
            "name": "اسپرسو دو شات",
            "description": "دو شات اسپرسو از دانه‌های تازه برشته‌شده اتیوپی یرگاچف.",
            "price": 85000,
            "badge": "ویژه باریستا",
            "tags": "قهوه,اسپرسو",
            "ingredients": "دانه قهوه اسپشیال، آب تصفیه‌شده",
            "calories": 5,
            "is_active": True,
            "is_featured": True,
            "is_full_time": True,
            "sort_order": 10,
        },
    )
    if not espresso.primary_image:
        espresso.primary_image.save(
            "espresso.jpg",
            make_image(COLORS["espresso"], "Espresso"),
            save=False,
        )
    espresso.save()

    latte, _ = MenuItem.objects.update_or_create(
        category=hot_drinks,
        slug="caramel-latte",
        defaults={
            "name": "لاته کاراملی",
            "description": "لاته تهیه‌شده با شیر محلی و سس کارامل خانگی.",
            "price": 125000,
            "discount_percent": 10,
            "tags": "قهوه,لاته,کارامل",
            "ingredients": "اسپرسو، شیر تازه، سس کارامل",
            "calories": 220,
            "is_active": True,
            "is_featured": True,
            "is_full_time": False,
            "available_days": "sat,sun,mon,tue,wed,thu",
            "available_from": time(10, 0),
            "available_to": time(22, 0),
            "sort_order": 20,
        },
    )
    if not latte.primary_image:
        latte.primary_image.save(
            "caramel_latte.jpg",
            make_image(COLORS["latte"], "Caramel Latte"),
            save=False,
        )
    latte.save()

    cheesecake, _ = MenuItem.objects.update_or_create(
        category=desserts,
        slug="raspberry-cheesecake",
        defaults={
            "name": "چیزکیک تمشک",
            "description": "چیزکیک تازه با سس خانگی تمشک جنگلی.",
            "price": 178000,
            "special_price": 165000,
            "tags": "دسر,چیزکیک",
            "ingredients": "پنیر ماسکارپونه، بیسکویت کره‌ای، تمشک تازه",
            "calories": 430,
            "is_active": True,
            "is_featured": False,
            "is_full_time": True,
            "sort_order": 5,
        },
    )
    if not cheesecake.primary_image:
        cheesecake.primary_image.save(
            "raspberry_cheesecake.jpg",
            make_image(COLORS["cheesecake"], "Raspberry"),
            save=False,
        )
    cheesecake.save()

    MenuItem.objects.filter(category__business=business).exclude(slug__in=desired_item_slugs).delete()

    for idx, caption in enumerate(["برش تازه", "سرو با تمشک"]):
        gallery_image, _ = MenuItemImage.objects.update_or_create(
            menu_item=cheesecake,
            order=idx,
            defaults={"caption": caption},
        )
        if not gallery_image.image:
            gallery_image.image.save(
                f"cheesecake_gallery_{idx + 1}.jpg",
                make_image(COLORS["cheesecake"], caption, size=(600, 400)),
                save=True,
            )

    # Remove extra gallery images
    cheesecake.gallery.exclude(order__in=[0, 1]).delete()

    print("Demo cafe and menu created successfully.")
    print("Credentials -> username: demo_owner | password: demo1234")


if __name__ == "__main__":
    create_demo_business()

