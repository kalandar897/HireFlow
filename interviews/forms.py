from django import forms
from .models import Interview


class InterviewForm(forms.ModelForm):

    interview_date = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={"type": "datetime-local"}
        )
    )

    class Meta:
        model = Interview
        fields = ["interview_date", "meeting_mode"]