# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from .models import User, SupportRequest


class RegisterForm(UserCreationForm):
    """User registration form (email-only login)."""

    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "First Name"}),
    )

    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "Last Name"}),
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "input", "placeholder": "Email Address"}
        )
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"class": "input", "placeholder": "Password"}),
    )

    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={"class": "input", "placeholder": "Confirm Password"}
        ),
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email


class LoginForm(forms.Form):
    """Login using email + password."""

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "input", "placeholder": "Email Address"}
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "input", "placeholder": "Password"})
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        user = authenticate(username=email, password=password)

        if not user:
            raise forms.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise forms.ValidationError("Your account is not active.")

        cleaned_data["user"] = user
        return cleaned_data


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]

        widgets = {
            "first_name": forms.TextInput(
                attrs={
                    "class": "w-full border px-3 py-2 rounded",
                    "placeholder": "First name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "class": "w-full border px-3 py-2 rounded",
                    "placeholder": "Last name",
                }
            ),
        }


class SupportForm(forms.ModelForm):
    """
    Support form for logged-in users.
    User's name and email are displayed but not editable.
    Only subject and message are submitted.
    """

    class Meta:
        model = SupportRequest
        fields = ["subject", "message"]
        widgets = {
            "subject": forms.TextInput(
                attrs={
                    "class": "w-full border px-3 py-2 rounded focus:outline-none focus:ring-2 focus:ring-[color:var(--color-primary)]/50",
                    "placeholder": "What can we help you with?",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "w-full border px-3 py-2 rounded focus:outline-none focus:ring-2 focus:ring-[color:var(--color-primary)]/50",
                    "placeholder": "Describe your issue or question...",
                    "rows": 6,
                }
            ),
        }
