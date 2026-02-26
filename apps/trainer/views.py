"""
Views for trainer app.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView, TemplateView

from apps.trainer.forms import SessionCreateForm, TurnSubmitForm
from apps.trainer.models import TrainingSession
from apps.trainer.services import SessionService, TurnSubmissionService


class SessionListView(LoginRequiredMixin, ListView):
    """List all training sessions for the current user."""

    model = TrainingSession
    template_name = "trainer/session_list.html"
    context_object_name = "sessions"

    def get_queryset(self):
        return SessionService.list_user_sessions(self.request.user)


class SessionCreateView(LoginRequiredMixin, View):
    """Create a new training session."""

    template_name = "trainer/session_create.html"

    def get(self, request):
        form = SessionCreateForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = SessionCreateForm(request.POST)
        if form.is_valid():
            session = SessionService.create_session(
                user=request.user,
                scenario=form.cleaned_data["scenario"],
                track=form.cleaned_data["track"],
                level=form.cleaned_data["level"],
                title=form.cleaned_data.get("title"),
            )
            messages.success(request, "Training session created successfully!")
            return redirect("trainer:session_workspace", session_id=session.id)
        return render(request, self.template_name, {"form": form})


class SessionWorkspaceView(LoginRequiredMixin, View):
    """Main training workspace view."""

    template_name = "trainer/session_workspace.html"

    def get(self, request, session_id):
        session = get_object_or_404(
            TrainingSession,
            id=session_id,
            user=request.user,
        )
        form = TurnSubmitForm()
        turns = session.turns.order_by("turn_index")
        latest_turn = turns.last()

        context = {
            "session": session,
            "form": form,
            "turns": turns,
            "latest_turn": latest_turn,
            "profile": request.user.profile,
        }
        return render(request, self.template_name, context)


class TurnSubmitView(LoginRequiredMixin, View):
    """Handle turn submission via HTMX."""

    def post(self, request, session_id):
        session = get_object_or_404(
            TrainingSession,
            id=session_id,
            user=request.user,
        )

        form = TurnSubmitForm(request.POST)
        if not form.is_valid():
            # Return form errors as HTML partial
            return render(
                request,
                "trainer/partials/_form_errors.html",
                {"form": form},
                status=400,
            )

        # Process the turn
        service = TurnSubmissionService()
        result = service.execute(
            session=session,
            user_input=form.cleaned_data["user_input"],
        )

        if not result.success:
            return render(
                request,
                "trainer/partials/_error_message.html",
                {"error_message": result.error_message},
                status=400,
            )

        # Return the feedback panel partial
        context = {
            "turn": result.turn,
            "session": session,
            "profile": request.user.profile,
        }

        # Check if this is an HTMX request
        if request.headers.get("HX-Request"):
            response = render(
                request,
                "trainer/partials/_feedback_panel.html",
                context,
            )
            # Trigger turn history update
            response["HX-Trigger"] = "turnSubmitted"
            return response

        # Full page reload fallback
        return redirect("trainer:session_workspace", session_id=session_id)


class TurnHistoryView(LoginRequiredMixin, View):
    """Get turn history partial for HTMX updates."""

    def get(self, request, session_id):
        session = get_object_or_404(
            TrainingSession,
            id=session_id,
            user=request.user,
        )
        turns = session.turns.order_by("turn_index")

        return render(
            request,
            "trainer/partials/_turn_history.html",
            {"turns": turns, "session": session},
        )


class SessionArchiveView(LoginRequiredMixin, View):
    """Archive a training session."""

    def post(self, request, session_id):
        session = get_object_or_404(
            TrainingSession,
            id=session_id,
            user=request.user,
        )
        SessionService.archive_session(session)
        messages.info(request, "Session archived.")
        return redirect("trainer:session_list")