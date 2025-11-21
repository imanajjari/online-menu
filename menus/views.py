import json
from collections import defaultdict

from django.contrib import messages
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import DetailView, TemplateView

from businesses.models import Business, BusinessHour
from .models import MenuCategory, MenuItem


class HomeView(TemplateView):
    template_name = "menus/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        businesses = Business.objects.order_by("name")
        if query:
            businesses = businesses.filter(
                Q(name__icontains=query)
                | Q(tagline__icontains=query)
                | Q(city__icontains=query)
                | Q(description__icontains=query)
            )
        featured_items = (
            MenuItem.objects.filter(is_active=True, is_featured=True)
            .select_related("category", "category__business")
            .order_by("-updated_at")[:6]
        )
        context.update(
            {
                "businesses": businesses,
                "featured_items": featured_items,
                "query": query,
            }
        )
        return context


class BusinessDetailView(TemplateView):
    template_name = "menus/business_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.get("slug")
        business = get_object_or_404(
            Business.objects.prefetch_related(
                Prefetch(
                    "categories",
                    queryset=MenuCategory.objects.filter(is_active=True).prefetch_related("items"),
                ),
                Prefetch(
                    "hours",
                    queryset=BusinessHour.objects.filter(is_visible=True),
                ),
            ),
            slug=slug,
        )
        query = self.request.GET.get("q", "").strip()
        now = timezone.localtime()
        categories_data = []
        total_items = 0
        for category in business.categories.all():
            items_qs = category.items.filter(is_active=True)
            if query:
                items_qs = items_qs.filter(
                    Q(name__icontains=query)
                    | Q(description__icontains=query)
                    | Q(tags__icontains=query)
                    | Q(badge__icontains=query)
                )
            visible_items = [item for item in items_qs if item.is_visible(now)]
            total_items += len(visible_items)
            categories_data.append(
                {
                    "category": category,
                    "items": visible_items,
                    "item_count": len(visible_items),
                }
            )
        notes = self.request.session.get("menu_notes", {})
        note_map = {}
        for key, value in notes.items():
            try:
                note_map[int(key)] = value
            except (TypeError, ValueError):
                continue
        context.update(
            {
                "business": business,
                "categories_data": categories_data,
                "query": query,
                "total_items": total_items,
                "notes": notes,
                "note_map": note_map,
                "note_count": len(note_map),
            }
        )
        return context


class ItemDetailView(DetailView):
    template_name = "menus/item_detail.html"
    context_object_name = "item"

    def get_queryset(self):
        return MenuItem.objects.filter(
            category__business__slug=self.kwargs.get("business_slug"),
            slug=self.kwargs.get("item_slug"),
            is_active=True,
        ).select_related("category", "category__business")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item = self.object
        business = item.category.business
        related_items = (
            MenuItem.objects.filter(category=item.category, is_active=True)
            .exclude(pk=item.pk)
            .order_by("sort_order")[:4]
        )
        notes = self.request.session.get("menu_notes", {})
        context.update(
            {
                "business": business,
                "related_items": related_items,
                "notes": notes,
            }
        )
        return context


class SearchView(TemplateView):
    template_name = "menus/search_results.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get("q", "").strip()
        business_slug = self.request.GET.get("business")
        items = MenuItem.objects.filter(is_active=True)
        if business_slug:
            items = items.filter(category__business__slug=business_slug)
        if query:
            items = items.filter(
                Q(name__icontains=query)
                | Q(description__icontains=query)
                | Q(tags__icontains=query)
                | Q(category__title__icontains=query)
                | Q(category__business__name__icontains=query)
            )
        items = items.select_related("category", "category__business").order_by("category__business__name", "sort_order")
        grouped = defaultdict(list)
        for item in items:
            if item.is_visible():
                grouped[item.category.business].append(item)
        grouped_list = sorted(grouped.items(), key=lambda entry: entry[0].name)
        context.update(
            {
                "query": query,
                "grouped_results": grouped_list,
                "business_filter": business_slug,
            }
        )
        return context


class NoteListView(TemplateView):
    template_name = "menus/notes.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        notes = self.request.session.get("menu_notes", {})
        item_ids = [int(pk) for pk in notes.keys()]
        items = MenuItem.objects.filter(pk__in=item_ids).select_related("category", "category__business")
        items_map = {item.pk: item for item in items}
        note_items = []
        for pk, data in notes.items():
            item = items_map.get(int(pk))
            if item:
                note_items.append({"item": item, "note": data.get("note"), "updated_at": data.get("updated_at")})
        context.update({"note_items": note_items})
        return context


class NoteAjaxMixin:
    @staticmethod
    def _is_ajax(request):
        return request.headers.get("x-requested-with") == "XMLHttpRequest"

    @staticmethod
    def _get_data(request):
        if request.content_type == "application/json":
            try:
                payload = json.loads(request.body.decode("utf-8")) if request.body else {}
            except json.JSONDecodeError:
                payload = {}
            return payload
        return request.POST


class AddNoteView(NoteAjaxMixin, View):
    def post(self, request, business_slug, item_id):
        business = get_object_or_404(Business, slug=business_slug)
        item = get_object_or_404(MenuItem, pk=item_id, category__business=business)
        data = self._get_data(request)
        note_text = (data.get("note") or "").strip()
        next_url = data.get("next") or item.get_absolute_url()
        notes = request.session.get("menu_notes", {})

        key = str(item.pk)
        if note_text:
            notes[key] = {
                "note": note_text,
                "updated_at": timezone.now().isoformat(),
                "business": business.name,
                "item_name": item.name,
            }
            message_text = "یادداشت ذخیره شد."
            has_note = True
            stored_note = note_text
        else:
            if key in notes:
                del notes[key]
            message_text = "یادداشت حذف شد."
            has_note = False
            stored_note = ""

        request.session["menu_notes"] = notes
        note_count = len(notes)

        if self._is_ajax(request):
            return JsonResponse(
                {
                    "success": True,
                    "has_note": has_note,
                    "note": stored_note,
                    "note_count": note_count,
                    "message": message_text,
                }
            )

        messages.success(request, message_text)
        return redirect(next_url)


class RemoveNoteView(NoteAjaxMixin, View):
    def post(self, request, business_slug, item_id):
        business = get_object_or_404(Business, slug=business_slug)
        item = get_object_or_404(MenuItem, pk=item_id, category__business=business)
        data = self._get_data(request)
        next_url = data.get("next") or reverse("menu:notes")

        notes = request.session.get("menu_notes", {})
        key = str(item.pk)
        removed = notes.pop(key, None)
        request.session["menu_notes"] = notes
        note_count = len(notes)

        if self._is_ajax(request):
            return JsonResponse(
                {
                    "success": True,
                    "has_note": False,
                    "note": "",
                    "note_count": note_count,
                    "message": "یادداشت حذف شد.",
                }
            )

        if removed:
            messages.success(request, "یادداشت حذف شد.")
        return redirect(next_url)


class ClearNotesView(View):
    def post(self, request):
        if "menu_notes" in request.session:
            del request.session["menu_notes"]
        messages.success(request, "یادداشت‌ها پاک شدند.")
        next_url = request.POST.get("next") or reverse("menu:notes")
        return redirect(next_url)
