import json

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import TemplateView

from businesses.forms import BusinessForm, BusinessHourFormSet
from businesses.models import Business, BusinessHour
from menus.forms import MenuCategoryForm, MenuItemForm, MenuItemImageFormSet
from menus.models import MenuCategory, MenuItem, MenuItemImage


class OwnerBusinessMixin(LoginRequiredMixin):
    login_url = "accounts:login"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        self.business = self.get_business()
        return super().dispatch(request, *args, **kwargs)

    def get_business(self):
        user = self.request.user
        defaults = {"name": f"کافه {user.get_full_name() or user.username}"}
        business, created = Business.objects.get_or_create(owner=user, defaults=defaults)
        if created:
            self._ensure_hours(business)
        return business

    def _ensure_hours(self, business):
        for code, _label in BusinessHour.DAYS_OF_WEEK:
            BusinessHour.objects.get_or_create(business=business, day_of_week=code)


class DashboardHomeView(OwnerBusinessMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        business = self.business
        items = MenuItem.objects.filter(category__business=business)
        context.update(
            {
                "business": business,
                "categories_count": business.categories.count(),
                "items_count": items.count(),
                "active_items": items.filter(is_active=True).count(),
                "featured_items": items.filter(is_featured=True).count(),
            }
        )
        return context


class BusinessProfileView(OwnerBusinessMixin, TemplateView):
    template_name = "dashboard/business_form.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        form = kwargs.get("form") or BusinessForm(instance=self.business)
        formset = kwargs.get("formset") or BusinessHourFormSet(instance=self.business)
        for form_hour in formset.forms:
            for name, field in form_hour.fields.items():
                classes = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = f"input-control {classes}".strip()
                if name in {"opens_at", "closes_at"}:
                    field.widget.attrs.setdefault("type", "time")
        context.update({"form": form, "formset": formset, "business": self.business})
        return context

    def post(self, request, *args, **kwargs):
        # Handle checkbox for show_hours (if not in POST, it's False)
        post_data = request.POST.copy()
        if 'show_hours' not in post_data:
            post_data['show_hours'] = False
        
        form = BusinessForm(post_data, request.FILES, instance=self.business)
        formset = BusinessHourFormSet(request.POST, instance=self.business)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "اطلاعات کسب‌وکار ذخیره شد.")
            return redirect("dashboard:business_edit")
        messages.error(request, "لطفا خطاهای فرم را بررسی کنید.")
        return self.render_to_response(self.get_context_data(form=form, formset=formset))


class CategoryListView(OwnerBusinessMixin, TemplateView):
    template_name = "dashboard/category_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "business": self.business,
            "categories": self.business.categories.all(),
        })
        return context


class CategoryCreateView(OwnerBusinessMixin, View):
    template_name = "dashboard/category_form.html"

    def get(self, request):
        form = MenuCategoryForm()
        return render(request, self.template_name, {"form": form, "business": self.business})

    def post(self, request):
        form = MenuCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save(commit=False)
            category.business = self.business
            category.save()
            messages.success(request, "دسته‌بندی جدید ایجاد شد.")
            return redirect("dashboard:category_list")
        messages.error(request, "لطفا خطاهای فرم را بررسی کنید.")
        return render(request, self.template_name, {"form": form, "business": self.business})


class CategoryUpdateView(OwnerBusinessMixin, View):
    template_name = "dashboard/category_form.html"

    def get_object(self, pk):
        return get_object_or_404(MenuCategory, pk=pk, business=self.business)

    def get(self, request, pk):
        category = self.get_object(pk)
        form = MenuCategoryForm(instance=category)
        return render(request, self.template_name, {"form": form, "business": self.business, "category": category})

    def post(self, request, pk):
        category = self.get_object(pk)
        form = MenuCategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "دسته‌بندی به‌روزرسانی شد.")
            return redirect("dashboard:category_list")
        messages.error(request, "لطفا خطاهای فرم را بررسی کنید.")
        return render(request, self.template_name, {"form": form, "business": self.business, "category": category})


class CategoryDeleteView(OwnerBusinessMixin, View):
    def post(self, request, pk):
        category = get_object_or_404(MenuCategory, pk=pk, business=self.business)
        category.delete()
        messages.success(request, "دسته‌بندی حذف شد.")
        return redirect("dashboard:category_list")


class ItemListView(OwnerBusinessMixin, TemplateView):
    template_name = "dashboard/item_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "business": self.business,
                "items": MenuItem.objects.filter(category__business=self.business).select_related("category"),
            }
        )
        return context


class ItemCreateView(OwnerBusinessMixin, View):
    template_name = "dashboard/item_form.html"

    def get(self, request):
        if not self.business.categories.exists():
            messages.info(request, "ابتدا یک دسته‌بندی بسازید.")
            return redirect("dashboard:category_create")
        form = MenuItemForm()
        form.fields["category"].queryset = self.business.categories.all()
        return render(request, self.template_name, {"form": form, "business": self.business})

    def post(self, request):
        if not self.business.categories.exists():
            messages.info(request, "ابتدا یک دسته‌بندی بسازید.")
            return redirect("dashboard:category_create")
        form = MenuItemForm(request.POST, request.FILES)
        form.fields["category"].queryset = self.business.categories.all()
        if form.is_valid():
            menu_item = form.save()
            gallery_files = request.FILES.getlist("gallery_images")
            for index, file in enumerate(gallery_files):
                MenuItemImage.objects.create(menu_item=menu_item, image=file, order=index)
            messages.success(request, "محصول جدید اضافه شد.")
            return redirect("dashboard:item_list")
        messages.error(request, "لطفا خطاهای فرم را بررسی کنید.")
        return render(request, self.template_name, {"form": form, "business": self.business})


class ItemUpdateView(OwnerBusinessMixin, View):
    template_name = "dashboard/item_form.html"

    def get_object(self, pk):
        return get_object_or_404(MenuItem, pk=pk, category__business=self.business)

    def get(self, request, pk):
        item = self.get_object(pk)
        form = MenuItemForm(instance=item)
        form.fields["category"].queryset = self.business.categories.all()
        formset = MenuItemImageFormSet(instance=item)
        self._style_gallery_formset(formset)
        return render(
            request,
            self.template_name,
            {"form": form, "formset": formset, "business": self.business, "item": item},
        )

    def post(self, request, pk):
        item = self.get_object(pk)
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        form.fields["category"].queryset = self.business.categories.all()
        formset = MenuItemImageFormSet(request.POST, request.FILES, instance=item)
        self._style_gallery_formset(formset)
        if form.is_valid() and formset.is_valid():
            menu_item = form.save()
            formset.save()
            gallery_files = request.FILES.getlist("gallery_images")
            start_index = menu_item.gallery.count()
            for idx, file in enumerate(gallery_files):
                MenuItemImage.objects.create(menu_item=menu_item, image=file, order=start_index + idx)
            messages.success(request, "محصول به‌روزرسانی شد.")
            return redirect("dashboard:item_list")
        messages.error(request, "لطفا خطاهای فرم را بررسی کنید.")
        return render(
            request,
            self.template_name,
            {"form": form, "formset": formset, "business": self.business, "item": item},
        )

    def _style_gallery_formset(self, formset):
        for gallery_form in formset.forms:
            for name, field in gallery_form.fields.items():
                classes = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = f"input-control {classes}".strip()


class ItemDeleteView(OwnerBusinessMixin, View):
    def post(self, request, pk):
        item = get_object_or_404(MenuItem, pk=pk, category__business=self.business)
        item.delete()
        messages.success(request, "محصول حذف شد.")
        return redirect("dashboard:item_list")


class MenuOrderView(OwnerBusinessMixin, TemplateView):
    template_name = "dashboard/menu_order.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = self.business.categories.all().order_by('order', 'id')
        categories_data = []
        for category in categories:
            items = category.items.all().order_by('sort_order', 'id')
            categories_data.append({
                'category': category,
                'items': items,
            })
        context.update({
            'business': self.business,
            'categories_data': categories_data,
        })
        return context


class UpdateCategoryOrderView(OwnerBusinessMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            category_orders = data.get('categories', [])
            
            for index, category_id in enumerate(category_orders):
                category = get_object_or_404(
                    MenuCategory, 
                    pk=category_id, 
                    business=self.business
                )
                category.order = index
                category.save()
            
            return JsonResponse({'success': True, 'message': 'ترتیب دسته‌بندی‌ها به‌روزرسانی شد'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)


class UpdateItemOrderView(OwnerBusinessMixin, View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            category_id = data.get('category_id')
            item_orders = data.get('items', [])
            
            category = get_object_or_404(
                MenuCategory,
                pk=category_id,
                business=self.business
            )
            
            for index, item_id in enumerate(item_orders):
                item = get_object_or_404(
                    MenuItem,
                    pk=item_id,
                    category=category
                )
                item.sort_order = index
                item.save()
            
            return JsonResponse({'success': True, 'message': 'ترتیب محصولات به‌روزرسانی شد'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
