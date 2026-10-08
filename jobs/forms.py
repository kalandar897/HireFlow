from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            "title",
            "company",
            "description",
            "location",
            "required_skills",
        ]

        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter job title"
            }),
            "company": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter company name"
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Enter job description",
                "rows": 5
            }),
            "location": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter job location"
            }),
            "required_skills": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Example: Python, Django, SQL",
                "rows": 3
            }),
        }