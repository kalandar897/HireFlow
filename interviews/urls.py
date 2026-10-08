from django.urls import path
from . import views

urlpatterns = [
    path(
        "schedule/<int:application_id>/",
        views.schedule_interview,
        name="schedule_interview"
    ),
    path(
        "my-interviews/",
        views.candidate_interviews,
        name="candidate_interviews"
    ),
    path(
        "recruiter-interviews/",
        views.recruiter_interviews,
        name="recruiter_interviews"
    ),  
    path(
        "update-status/<int:interview_id>/",
        views.update_interview_status,
        name="update_interview_status"
    ),
]