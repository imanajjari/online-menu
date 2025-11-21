from django.urls import path

from .views import (
    BusinessProfileView,
    CategoryCreateView,
    CategoryDeleteView,
    CategoryListView,
    CategoryUpdateView,
    DashboardHomeView,
    ItemCreateView,
    ItemDeleteView,
    ItemListView,
    ItemUpdateView,
    MenuOrderView,
    UpdateCategoryOrderView,
    UpdateItemOrderView,
)


app_name = "dashboard"

urlpatterns = [
    path("", DashboardHomeView.as_view(), name="home"),
    path("profile/", BusinessProfileView.as_view(), name="business_edit"),
    path("menu-order/", MenuOrderView.as_view(), name="menu_order"),
    path("menu-order/categories/", UpdateCategoryOrderView.as_view(), name="update_category_order"),
    path("menu-order/items/", UpdateItemOrderView.as_view(), name="update_item_order"),
    path("categories/", CategoryListView.as_view(), name="category_list"),
    path("categories/new/", CategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/edit/", CategoryUpdateView.as_view(), name="category_edit"),
    path("categories/<int:pk>/delete/", CategoryDeleteView.as_view(), name="category_delete"),
    path("items/", ItemListView.as_view(), name="item_list"),
    path("items/new/", ItemCreateView.as_view(), name="item_create"),
    path("items/<int:pk>/edit/", ItemUpdateView.as_view(), name="item_edit"),
    path("items/<int:pk>/delete/", ItemDeleteView.as_view(), name="item_delete"),
]

