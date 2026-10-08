import os
from django import forms
from .models import Application

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["resume", "cover_letter"]

        widgets = {
            "cover_letter": forms.Textarea(attrs={
                "rows": 5,
                "placeholder": "Write your cover letter here...",
            }),
        }

    def clean_resume(self):
        resume = self.cleaned_data.get("resume")

        # Resume is optional in your current model
        if not resume or not hasattr(resume, "size"):
            return resume

        # Allow only PDF, DOC, and DOCX files
        allowed_extensions = [".pdf", ".doc", ".docx"]
        extension = os.path.splitext(resume.name)[1].lower()

        if extension not in allowed_extensions:
            raise forms.ValidationError(
                "Upload your resume in PDF, DOC, or DOCX format."
            )

        # Maximum file size: 5 MB
        if resume.size > 5 * 1024 * 1024:
            raise forms.ValidationError(
                "Resume size must not exceed 5 MB."
            )

        return resume