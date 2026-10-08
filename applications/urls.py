from django.urls import path
from . import views

urlpatterns = [
    path(
        "candidate/dashboard/",
        views.candidate_dashboard,
        name="candidate_dashboard"
    ),
    path(
        "apply/<int:job_id>/", 
        views.apply_job, 
        name="apply_job"
    ),
    path(
        "recruiter/applications/",
        views.recruiter_applications,
        name="recruiter_applications"
    ),
    path(
        "recruiter/applications/<int:application_id>/status/",
        views.update_application_status,
        name="update_application_status"
    ), 
    path(
        "update-result/<int:application_id>/",
        views.update_application_result,
        name="update_application_result"
    ),
    path(
        "recruiter/applications/<int:application_id>/candidate-profile/",
        views.view_candidate_profile,
        name="view_candidate_profile",
    ),
]