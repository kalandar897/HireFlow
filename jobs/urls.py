from django.urls import path
from . import views

urlpatterns = [
    path("", views.job_list, name="job_list"),
    path(
        "recruiter/dashboard/",
        views.recruiter_dashboard,
        name="recruiter_dashboard"
    ),
    path(
        "recruiter/applications/",
        views.recruiter_all_applications,
        name="recruiter_all_applications",
    ),
    path(
        "create/",
        views.create_job, 
        name="create_job"
    ),
    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),
    path(
        "admin-dashboard/jobs/<int:job_id>/toggle/",
        views.toggle_job_status,
        name="toggle_job_status",
    ),  
    path(
        "admin-dashboard/users/<int:user_id>/toggle/",
        views.toggle_user_status,
        name="toggle_user_status",
    ),
    path(
        "recruiter/jobs/<int:job_id>/edit/",
        views.edit_job,
        name="edit_job",
    ),
    path(
        "recruiter/jobs/<int:job_id>/toggle/",
        views.toggle_recruiter_job_status,
        name="toggle_recruiter_job_status",
    ),
    path(
        "export-applications/",
        views.export_applications_csv,
        name="export_applications_csv"
    ),
    path(
        "recruiter/export-applications/",
        views.export_recruiter_applications_csv,
        name="export_recruiter_applications_csv",
    ),
]