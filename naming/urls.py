from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("resources/", views.resource_list, name="resource_list"),
    path("resources/new/", views.resource_create, name="resource_create"),
    path("resources/<int:pk>/", views.resource_detail, name="resource_detail"),
    path("resources/<int:pk>/edit/", views.resource_edit, name="resource_edit"),
    path("resources/<int:pk>/delete/", views.resource_delete, name="resource_delete"),
    path("groups/", views.group_list, name="group_list"),
    path("groups/new/", views.group_create, name="group_create"),
    path("groups/<int:pk>/", views.group_detail, name="group_detail"),
    path("groups/<int:pk>/edit/", views.group_edit, name="group_edit"),
    path("groups/<int:pk>/delete/", views.group_delete, name="group_delete"),
    path("vocabulary/", views.vocabulary_manage, name="vocabulary_manage"),
    path("api/next-instance/", views.api_next_instance, name="api_next_instance"),
]
