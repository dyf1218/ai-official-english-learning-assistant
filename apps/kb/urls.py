"""
URL configuration for knowledge base app.
"""

from django.urls import path

from apps.kb import views

app_name = "kb"

urlpatterns = [
    path("", views.TemplateListView.as_view(), name="template_list"),
    path("save/", views.TemplateSaveView.as_view(), name="template_save"),
    path(
        "<uuid:template_id>/",
        views.TemplateDetailView.as_view(),
        name="template_detail",
    ),
    path(
        "<uuid:template_id>/delete/",
        views.TemplateDeleteView.as_view(),
        name="template_delete",
    ),
]