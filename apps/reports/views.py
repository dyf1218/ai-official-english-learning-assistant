"""
Views for reports app.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

from apps.reports.services import ReportService


class WeeklySummaryView(LoginRequiredMixin, View):
    """Display weekly summary report."""

    template_name = "reports/weekly_summary.html"

    def get(self, request):
        # Get the latest report
        latest_report = ReportService.get_latest_report(request.user)

        # Get date bounds for context
        current_start, current_end = ReportService.get_current_week_bounds()
        last_start, last_end = ReportService.get_last_week_bounds()

        context = {
            "report": latest_report,
            "current_week": {"start": current_start, "end": current_end},
            "last_week": {"start": last_start, "end": last_end},
        }

        return render(request, self.template_name, context)


class GenerateReportView(LoginRequiredMixin, View):
    """Generate a new weekly report on demand."""

    def post(self, request):
        # Generate report for last week
        period_start, period_end = ReportService.get_last_week_bounds()

        report = ReportService.generate_weekly_report(
            user=request.user,
            period_start=period_start,
            period_end=period_end,
        )

        # Return partial for HTMX
        if request.headers.get("HX-Request"):
            return render(
                request,
                "reports/partials/_report_content.html",
                {"report": report},
            )

        # Redirect for full page request
        from django.shortcuts import redirect
        return redirect("reports:weekly_summary")