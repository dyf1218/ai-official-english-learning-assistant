"""
URL configuration for reports app.
"""

from django.urls import path

from apps.reports import views

app_name = "reports"

urlpatterns = [
    path("weekly/", views.WeeklySummaryView.as_view(), name="weekly_summary"),
    path("generate/", views.GenerateReportView.as_view(), name="generate_report"),
]