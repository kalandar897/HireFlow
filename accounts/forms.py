import os
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .models import CandidateProfile


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    role = forms.ChoiceField(
        choices=[
            ("CANDIDATE", "Candidate"),
            ("RECRUITER", "Recruiter"),
        ]
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "role",
            "password1",
            "password2",
        ]

class CandidateProfileForm(forms.ModelForm):
    class Meta:
        model = CandidateProfile
        fields = [
            "full_name",
            "phone",
            "education",
            "skills",
            "experience",
            "resume",
        ]

        widgets = {
            "full_name": forms.TextInput(attrs={
                "placeholder": "Enter your full name"
            }),
            "phone": forms.TextInput(attrs={
                "placeholder": "Enter your phone number"
            }),
            "education": forms.TextInput(attrs={
                "placeholder": "Example: BCA, MCA, B.Tech"
            }),
            "skills": forms.Textarea(attrs={
                "rows": 4,
                "placeholder": "Example: Python, Django, SQL, HTML, CSS"
            }),
            "experience": forms.TextInput(attrs={
                "placeholder": "Example: Fresher or 1 year"
            }),
        }
        
    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "").strip()

        if phone and not phone.replace("+", "").isdigit():
            raise forms.ValidationError(
                "Enter a valid phone number using digits and an optional +."
            )

        if phone and len(phone.replace("+", "")) < 10:
            raise forms.ValidationError(
                "Phone number must contain at least 10 digits."
            )

        return phone

    def clean_resume(self):
        resume = self.cleaned_data.get("resume")

        if not resume:
            return resume

        allowed_extensions = [".pdf", ".doc", ".docx"]
        extension = os.path.splitext(resume.name)[1].lower()

        if extension not in allowed_extensions:
            raise forms.ValidationError(
                "Upload your resume in PDF, DOC, or DOCX format."
            )

        if resume.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                "Resume size must not exceed 5 MB."
            )

        return resume