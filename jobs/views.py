from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from .models import Job
from .forms import JobForm
from applications.models import Application
from interviews.models import Interview
from django.db.models import Count, Q
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
import csv
from django.http import HttpResponse

# Create your views here.

@role_required("RECRUITER")
def recruiter_dashboard(request):

    jobs = Job.objects.filter(
        recruiter=request.user
    ).order_by("-created_at")

    applications = Application.objects.filter(
        job__recruiter=request.user
    )

    stats = {
        "total_jobs": jobs.count(),
        "total_applications": applications.count(),
        "shortlisted": applications.filter(
            status="SHORTLISTED"
        ).count(),
        "selected": applications.filter(
            status="SELECTED"
        ).count(),
        "rejected": applications.filter(
            status="REJECTED"
        ).count(),
        "total_interviews": Interview.objects.filter(
            application__job__recruiter=request.user
        ).count(),
    }
    application_status_data = list(
        applications.values("status")
        .annotate(total=Count("id"))
        .order_by("status")
    )

    job_application_data = list(
        jobs.annotate(
            application_count=Count("application")
        ).values("title", "application_count"),
    )
    recent_applications = Application.objects.filter(
        job__recruiter=request.user
    ).select_related(
        "candidate", "job"
    ).order_by("-applied_at")[:5]

    return render(
        request,
        "dashboard/recruiter.html",
        {"jobs": jobs, 
         "stats": stats,
         "application_status_data": application_status_data,
         "job_application_data": job_application_data,
         "recent_applications": recent_applications,}
    )

def job_list(request):
    jobs = Job.objects.filter(is_active=True)

    search_query = request.GET.get("q", "").strip()
    location_query = request.GET.get("location", "").strip()

    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(company__icontains=search_query)
            | Q(required_skills__icontains=search_query)
        )

    if location_query:
        jobs = jobs.filter(
            location__icontains=location_query
        )

    jobs = jobs.order_by("-created_at")

    return render(
        request,
        "jobs/job_list.html",
        {
            "jobs": jobs,
            "search_query": search_query,
            "location_query": location_query,
        },
    )

@role_required("RECRUITER")
def create_job(request):

    if request.method == "POST":
        form = JobForm(request.POST)

        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            messages.success(request, "Job posted successfully.")
            return redirect("recruiter_dashboard")
    else:
        form = JobForm()

    return render(
        request,
        "jobs/job_form.html",
        {"form": form}
    )


@role_required("RECRUITER")
def edit_job(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id,
        recruiter=request.user
    )

    if request.method == "POST":
        form = JobForm(request.POST, instance=job)

        if form.is_valid():
            form.save()
            messages.success(request, "Job updated successfully!")
            return redirect("recruiter_dashboard")
    else:
        form = JobForm(instance=job)

    return render(
        request,
        "jobs/edit_job.html",
        {"form": form, "job": job}
    )

@login_required
def admin_dashboard(request):
    if request.user.role != "ADMIN" and not request.user.is_superuser:
        raise PermissionDenied

    User = get_user_model()

    users = User.objects.all()
    user_query = request.GET.get("user_q", "").strip()
    role_filter = request.GET.get("role", "").strip()

    if user_query:
        users = users.filter(
            Q(username__icontains=user_query)
            | Q(email__icontains=user_query)
        )

    if role_filter in ["CANDIDATE", "RECRUITER", "ADMIN"]:
        users = users.filter(role=role_filter)

    users = users.order_by("-id")
    users = Paginator(users, 10).get_page(
        request.GET.get("users_page")
)

    jobs = Job.objects.select_related("recruiter")
    job_query = request.GET.get("job_q", "").strip()
    job_status = request.GET.get("job_status", "").strip()

    if job_query:
        jobs = jobs.filter(
            Q(title__icontains=job_query)
            | Q(company__icontains=job_query)
        )

    if job_status == "ACTIVE":
        jobs = jobs.filter(is_active=True)
    elif job_status == "CLOSED":
        jobs = jobs.filter(is_active=False)

    jobs = jobs.order_by("-created_at")
    jobs = Paginator(jobs, 10).get_page(
        request.GET.get("jobs_page"))

    all_users = User.objects.all()
    all_jobs = Job.objects.all()
    applications = Application.objects.select_related(
        "candidate", "job"
    ).order_by("-applied_at")

    applications = Paginator(applications, 10).get_page(
        request.GET.get("applications_page")
    )

    interviews = Interview.objects.select_related(
        "application__candidate",
        "application__job"
    ).order_by("-interview_date")

    interviews = Paginator(interviews, 10).get_page(
        request.GET.get("interviews_page")
    )

    stats = {
        "total_users": all_users.count(),
        "total_candidates": all_users.filter(role="CANDIDATE").count(),
        "total_recruiters": all_users.filter(role="RECRUITER").count(),
        "total_jobs": all_jobs.count(),
        "active_jobs": all_jobs.filter(is_active=True).count(),

        "total_applications": Application.objects.count(),
        "selected": Application.objects.filter(status="SELECTED").count(),
        "rejected": Application.objects.filter(status="REJECTED").count(),
        "shortlisted": Application.objects.filter(status="SHORTLISTED").count(),

        "total_interviews": Interview.objects.count(),
    }

    application_status_data = list(
        Application.objects.values("status")
        .annotate(total=Count("id"))
        .order_by("status")
    )

    return render(
        request,
        "dashboard/admin.html",
        {
            "stats": stats,
            "users": users,
            "jobs": jobs,
            "applications": applications,
            "interviews": interviews,
            "application_status_data": application_status_data,
            "user_query": user_query,
            "role_filter": role_filter,
            "job_query": job_query,
            "job_status": job_status,
        },
    )

@login_required
@require_POST
def toggle_job_status(request, job_id):
    if request.user.role != "ADMIN" and not request.user.is_superuser:
        raise PermissionDenied

    job = get_object_or_404(Job, id=job_id)

    job.is_active = not job.is_active
    job.save(update_fields=["is_active"])

    if job.is_active:
        messages.success(request, f"{job.title} is now active.")
    else:
        messages.success(request, f"{job.title} has been closed.")

    return redirect("admin_dashboard")


@login_required
@require_POST
def toggle_user_status(request, user_id):
    if request.user.role != "ADMIN" and not request.user.is_superuser:
        raise PermissionDenied

    User = get_user_model()
    target_user = get_object_or_404(User, id=user_id)

    if target_user.id == request.user.id:
        messages.error(request, "You cannot deactivate your own account.")
        return redirect("admin_dashboard")

    if target_user.is_superuser:
        messages.error(request, "Superuser accounts cannot be changed here.")
        return redirect("admin_dashboard")

    target_user.is_active = not target_user.is_active
    target_user.save(update_fields=["is_active"])

    if target_user.is_active:
        messages.success(
            request,
            f"{target_user.username} has been activated."
        )
    else:
        messages.success(
            request,
            f"{target_user.username} has been deactivated."
        )

    return redirect("admin_dashboard")

@role_required("RECRUITER")
@require_POST
def toggle_recruiter_job_status(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id,
        recruiter=request.user
    )

    job.is_active = not job.is_active
    job.save(update_fields=["is_active"])

    if job.is_active:
        messages.success(request, "Job reopened successfully.")
    else:
        messages.success(request, "Job closed successfully.")

    return redirect("recruiter_dashboard")


@login_required
def export_applications_csv(request):
    if request.user.role != "ADMIN" and not request.user.is_superuser:
        raise PermissionDenied

    applications = Application.objects.select_related(
        "candidate", "job"
    ).order_by("-applied_at")

    response = HttpResponse(
        content_type="text/csv"
    )
    response["Content-Disposition"] = (
        'attachment; filename="hireflow_applications.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        "Candidate",
        "Email",
        "Job Title",
        "Company",
        "Application Status",
        "Applied Date",
    ])

    for application in applications:
        writer.writerow([
            application.candidate.username,
            application.candidate.email,
            application.job.title,
            application.job.company,
            application.status,
            application.applied_at.strftime("%Y-%m-%d"),
        ])

    return response


@login_required
def recruiter_all_applications(request):
    if request.user.role != "RECRUITER":
        raise PermissionDenied

    applications = Application.objects.filter(
        job__recruiter=request.user
    ).select_related(
        "candidate", "job"
    ).order_by("-applied_at")

    # Search applications
    search_query = request.GET.get("q", "").strip()

    if search_query:
        applications = applications.filter(
            Q(candidate__username__icontains=search_query)
            | Q(candidate__email__icontains=search_query)
            | Q(job__title__icontains=search_query)
        )

    # Filter by application status
    status_filter = request.GET.get("status", "").strip()

    if status_filter in [
        "APPLIED", "SHORTLISTED", "INTERVIEW",
        "SELECTED", "REJECTED"
    ]:
        applications = applications.filter(
            status=status_filter
        )

    # Show 10 applications per page
    applications = Paginator(
        applications, 10
    ).get_page(request.GET.get("page"))

    return render(
        request,
        "dashboard/recruiter_applications.html",
        {
            "applications": applications,
            "search_query": search_query,
            "status_filter": status_filter,
        },
    )


@login_required
def export_recruiter_applications_csv(request):
    if request.user.role != "RECRUITER":
        raise PermissionDenied

    applications = Application.objects.filter(
        job__recruiter=request.user
    ).select_related(
        "candidate", "job"
    ).order_by("-applied_at")

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = (
        'attachment; filename="my_recruiter_applications.csv"'
    )

    writer = csv.writer(response)

    writer.writerow([
        "Candidate",
        "Email",
        "Job Title",
        "Company",
        "Application Status",
        "Applied Date",
        "Cover Letter",
    ])

    for application in applications:
        writer.writerow([
            application.candidate.username,
            application.candidate.email,
            application.job.title,
            application.job.company,
            application.status,
            application.applied_at.strftime("%Y-%m-%d"),
            application.cover_letter,
        ])

    return response