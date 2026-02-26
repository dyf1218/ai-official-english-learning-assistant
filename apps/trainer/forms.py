"""
Forms for trainer app.
"""

from django import forms

from apps.common.constants import Level, Scenario, Track
from apps.trainer.models import TrainingSession


class SessionCreateForm(forms.ModelForm):
    """Form for creating a new training session."""

    class Meta:
        model = TrainingSession
        fields = ["track", "scenario", "level", "title"]
        widgets = {
            "track": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "scenario": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "level": forms.Select(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                }
            ),
            "title": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500",
                    "placeholder": "Optional: Give your session a title",
                }
            ),
        }


class TurnSubmitForm(forms.Form):
    """Form for submitting a training turn."""

    user_input = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[200px]",
                "placeholder": "Enter your text here...",
                "rows": 8,
            }
        ),
        min_length=10,
        max_length=5000,
    )

    def clean_user_input(self):
        """Validate user input."""
        user_input = self.cleaned_data["user_input"].strip()
        if len(user_input) < 10:
            raise forms.ValidationError("Please enter at least 10 characters.")
        return user_input