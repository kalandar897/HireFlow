from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Application
from django.contrib import messages
from notifications.utils import create_notification
from jobs.models import Job
from .forms import ApplicationForm
from django.core.mail import send_mail
import os
from interviews.models import Interview
from django.db.models import Q

# Create your views here.

def validate_resume_file(resume):
    if not resume:
        return

    allowed_extensions = {".pdf", ".doc", ".docx"}
    extension = os.path.splitext(resume.name)[1].lower()

    if extension not in allowed_extensions:
        raise ValidationError(
            "Resume must be a PDF, DOC, or DOCX file."
        )

    if resume.size > 5 * 1024 * 1024:
        raise ValidationError(
            "Resume must not exceed 5 MB."
        )


@role_required("CANDIDATE")
def candidate_dashboard(request):

    applications = Application.objects.filter(
        candidate=request.user
    ).select_related("job").order_by("-applied_at")

    stats = {
        "total": applications.count(),
        "applied": applications.filter(status="APPLIED").count(),
        "shortlisted": applications.filter(status="SHORTLISTED").count(),
        "interview": applications.filter(status="INTERVIEW").count(),
        "selected": applications.filter(status="SELECTED").count(),
        "rejected": applications.filter(status="REJECTED").count(),
    }

    interviews = Interview.objects.filter(
        application__candidate=request.user
    ).select_related(
        "application__job"
    ).order_by("interview_date")

    return render(
        request,
        "dashboard/candidate.html",
        {
            "applications": applications,
            "stats": stats,
            "interviews": interviews,
        },
    )

@role_required("CANDIDATE")
def apply_job(request, job_id):

    job = get_object_or_404(
        Job,
        id=job_id,
        is_active=True
    )

    already_applied = Application.objects.filter(
        candidate=request.user,
        job=job
    ).exists()

    if already_applied:
        messages.warning(
            request,
            "You have already applied for this job."
        )
        return redirect("job_list")

    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)

        if form.is_valid():
            application = form.save(commit=False)
            application.candidate = request.user
            application.job = job
            application.save()

            messages.success(
                request,
                "Your application was submitted successfully!"
            )
            return redirect("candidate_dashboard")
    else:
        form = ApplicationForm()

    return render(
        request,
        "applications/apply.html",
        {
            "form": form,
            "job": job,
        }
    )


@role_required("RECRUITER")
def recruiter_applications(request):

    applications = Application.objects.filter(
        job__recruiter=request.user
    ).select_related(
        "candidate", "job"
    )

    search_query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()

    if search_query:
        applications = applications.filter(
            Q(candidate__username__icontains=search_query)
            | Q(candidate__email__icontains=search_query)
            | Q(job__title__icontains=search_query)
        )

    allowed_statuses = [
        "APPLIED",
        "SHORTLISTED",
        "INTERVIEW",
        "SELECTED",
        "REJECTED",
    ]

    if status_filter in allowed_statuses:
        applications = applications.filter(status=status_filter)

    applications = applications.order_by("-applied_at")

    return render(
        request,
        "applications/recruiter_applications.html",
        {
            "applications": applications,
            "search_query": search_query,
            "status_filter": status_filter,
        },
    )

@role_required("RECRUITER")
@require_POST
def update_application_status(request, application_id):

    application = get_object_or_404(
        Application,
        id=application_id,
        job__recruiter=request.user
    )

    allowed_statuses = [
        "SHORTLISTED",
        "INTERVIEW",
        "SELECTED",
        "REJECTED",
    ]

    new_status = request.POST.get("status")

    if new_status in allowed_statuses:
        application.status = new_status
        application.save(update_fields=["status"])

    return redirect("recruiter_applications")


@login_required
def update_application_result(request, application_id):
    if request.user.role != "RECRUITER":
        raise PermissionDenied

    application = get_object_or_404(
        Application,
        id=application_id,
        job__recruiter=request.user
    )

    if request.method == "POST":
        new_status = request.POST.get("status")
        allowed_statuses = ["SELECTED", "REJECTED"]

        if new_status in allowed_statuses:
            application.status = new_status
            application.save(update_fields=["status"])
                        
            if new_status == "SELECTED":
                create_notification(
                    application.candidate,
                    f"Congratulations! You have been selected for {application.job.title}."
                )
            elif new_status == "REJECTED":
                create_notification(
                    application.candidate,
                    f"Your application for {application.job.title} has been rejected."
                )

            subject = f"Application Update - {application.job.title}"

            if new_status == "SELECTED":
                message = (
                    f"Hello {application.candidate.username},\n\n"
                    f"Congratulations! You have been selected for "
                    f"{application.job.title}.\n\n"
                    "Regards,\nHireFlow Team"
                )
            else:
                message = (
                    f"Hello {application.candidate.username},\n\n"
                    f"Your application for {application.job.title} "
                    "was not selected this time.\n\n"
                    "Thank you for applying.\nHireFlow Team"
                )

            if application.candidate.email:
                send_mail(
                    subject,
                    message,
                    None,
                    [application.candidate.email],
                    fail_silently=False,
                )
                messages.success(
                    request,
                    "Application status updated and email notification processed."
                )
            else:
                messages.warning(
                    request,
                    "Status updated, but the candidate has no email address."
                )
        else:
            messages.error(request, "Invalid application status.")

    return redirect("recruiter_applications")

@login_required
def view_candidate_profile(request, application_id):
    from django.core.exceptions import PermissionDenied
    from accounts.models import CandidateProfile

    if request.user.role != "RECRUITER":
        raise PermissionDenied

    application = get_object_or_404(
        Application,
        id=application_id,
        job__recruiter=request.user
    )

    profile = CandidateProfile.objects.filter(
        user=application.candidate
    ).first()

    return render(
        request,
        "applications/candidate_profile_detail.html",
        {
            "application": application,
            "profile": profile,
        }
    )