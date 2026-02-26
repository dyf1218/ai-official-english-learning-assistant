"""
Views for accounts app.
"""

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView

from apps.accounts.forms import LoginForm, UserRegistrationForm


class RegisterView(View):
    """User registration view."""

    template_name = "accounts/register.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("trainer:session_list")
        form = UserRegistrationForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to SE English Trainer.")
            return redirect("trainer:session_list")
        return render(request, self.template_name, {"form": form})


class LoginView(View):
    """User login view."""

    template_name = "accounts/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("trainer:session_list")
        form = LoginForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get("next", "trainer:session_list")
                return redirect(next_url)
            else:
                messages.error(request, "Invalid username or password.")
        return render(request, self.template_name, {"form": form})


class LogoutView(View):
    """User logout view."""

    def get(self, request):
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect("home")

    def post(self, request):
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect("home")


class AccountView(LoginRequiredMixin, TemplateView):
    """User account settings view."""

    template_name = "accounts/account.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.request.user.profile
        return context