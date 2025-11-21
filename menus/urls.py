from django.urls import path, register_converter

from .views import (
    AddNoteView,
    BusinessDetailView,
    ClearNotesView,
    HomeView,
    ItemDetailView,
    NoteListView,
    RemoveNoteView,
    SearchView,
)


class UnicodeSlugConverter:
    regex = r'[-\w]+'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(UnicodeSlugConverter, "uslug")


app_name = "menu"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("search/", SearchView.as_view(), name="search"),
    path("notes/", NoteListView.as_view(), name="notes"),
    path("notes/clear/", ClearNotesView.as_view(), name="notes_clear"),
    path("<uslug:business_slug>/note/<int:item_id>/add/", AddNoteView.as_view(), name="add_note"),
    path("<uslug:business_slug>/note/<int:item_id>/remove/", RemoveNoteView.as_view(), name="remove_note"),
    path("<uslug:business_slug>/item/<uslug:item_slug>/", ItemDetailView.as_view(), name="item_detail"),
    path("<uslug:slug>/", BusinessDetailView.as_view(), name="business_detail"),
]

