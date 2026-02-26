"""
Views for knowledge base app.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView

from apps.common.constants import Scenario
from apps.kb.models import UserKBCard
from apps.kb.services import TemplateService


class TemplateListView(LoginRequiredMixin, ListView):
    """List all templates for the current user."""

    model = UserKBCard
    template_name = "kb/template_list.html"
    context_object_name = "templates"

    def get_queryset(self):
        queryset = TemplateService.list_templates(self.request.user)
        
        # Filter by scenario if provided
        scenario = self.request.GET.get("scenario")
        if scenario:
            queryset = queryset.filter(scenario=scenario)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["scenarios"] = Scenario.choices
        context["selected_scenario"] = self.request.GET.get("scenario", "")
        return context


class TemplateSaveView(LoginRequiredMixin, View):
    """Save a template from a training session."""

    def post(self, request):
        session_id = request.POST.get("session_id")
        turn_id = request.POST.get("turn_id")
        content = request.POST.get("template_content")
        scenario = request.POST.get("scenario")
        title = request.POST.get("title")

        if not content or not scenario:
            if request.headers.get("HX-Request"):
                return render(
                    request,
                    "kb/partials/_save_error.html",
                    {"error": "Content and scenario are required."},
                    status=400,
                )
            messages.error(request, "Content and scenario are required.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        # Save the template
        metadata = {}
        if session_id:
            metadata["session_id"] = session_id
        if turn_id:
            metadata["turn_id"] = turn_id

        template = TemplateService.save_template(
            user=request.user,
            scenario=scenario,
            content=content,
            title=title,
            metadata=metadata,
        )

        if request.headers.get("HX-Request"):
            return render(
                request,
                "kb/partials/_save_success.html",
                {"template": template},
            )

        messages.success(request, "Template saved successfully!")
        return redirect(request.META.get("HTTP_REFERER", "kb:template_list"))


class TemplateDeleteView(LoginRequiredMixin, View):
    """Delete a user's template."""

    def post(self, request, template_id):
        success = TemplateService.delete_template(template_id, request.user)

        if request.headers.get("HX-Request"):
            if success:
                return HttpResponse("", status=200)
            return HttpResponse("Template not found", status=404)

        if success:
            messages.success(request, "Template deleted.")
        else:
            messages.error(request, "Template not found.")

        return redirect("kb:template_list")


class TemplateDetailView(LoginRequiredMixin, View):
    """View template details."""

    def get(self, request, template_id):
        template = TemplateService.get_template(template_id, request.user)
        
        if not template:
            messages.error(request, "Template not found.")
            return redirect("kb:template_list")

        return render(
            request,
            "kb/template_detail.html",
            {"template": template},
        )