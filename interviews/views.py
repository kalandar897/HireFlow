from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from accounts.decorators import role_required
from applications.models import Application
from .forms import InterviewForm
from .models import Interview
from notifications.utils import create_notification

# Create your views here.

@role_required("RECRUITER")
def schedule_interview(request, application_id):

    application = get_object_or_404(
        Application,
        id=application_id,
        job__recruiter=request.user,
        status="SHORTLISTED"
    )

    if request.method == "POST":
        form = InterviewForm(request.POST)

        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = application
            interview.save()
            
            create_notification(
                application.candidate,
                f"Your interview for {application.job.title} has been scheduled "
                f"on {interview.interview_date.strftime('%d %b %Y at %I:%M %p')}. "
                f"Meeting mode: {interview.meeting_mode}."
            )

            candidate = application.candidate

            if candidate.email:
                send_mail(
                    subject=f"Interview Scheduled - {application.job.title}",
                    message=(
                        f"Hello {candidate.username},\n\n"
                        f"Your interview for {application.job.title} has been scheduled.\n\n"
                        f"Date and Time: {interview.interview_date:%d %b %Y, %I:%M %p}\n"
                        f"Meeting Mode: {interview.get_meeting_mode_display()}\n\n"
                        "Please be prepared for your interview.\n\n"
                        "Regards,\nHireFlow Team"
                    ),
                    from_email=None,
                    recipient_list=[candidate.email],
                    fail_silently=False,
                )

            messages.success(
                request,
                "Interview scheduled successfully!"
            )
            return redirect("recruiter_applications")
    else:
        form = InterviewForm()

    return render(
        request,
        "interviews/schedule_interview.html",
        {"form": form, "application": application}
    )


@role_required("CANDIDATE")
def candidate_interviews(request):

    interviews = Interview.objects.filter(
        application__candidate=request.user
    ).select_related(
        "application",
        "application__job"
    ).order_by("interview_date")

    return render(
        request,
        "interviews/candidate_interviews.html",
        {"interviews": interviews}
    )


@login_required
def recruiter_interviews(request):
    if request.user.role != "RECRUITER":
        raise PermissionDenied

    interviews = Interview.objects.filter(
        application__job__recruiter=request.user
    ).select_related(
        "application",
        "application__candidate",
        "application__job"
    ).order_by("interview_date")

    return render(
        request,
        "interviews/recruiter_interviews.html",
        {"interviews": interviews}
    )


@role_required("RECRUITER")
def update_interview_status(request, interview_id):

    interview = get_object_or_404(
        Interview,
        id=interview_id,
        application__job__recruiter=request.user
    )

    if request.method == "POST":
        new_status = request.POST.get("status")

        allowed_statuses = ["COMPLETED", "CANCELLED"]

        if new_status in allowed_statuses:
            interview.status = new_status
            interview.save(update_fields=["status"])
            messages.success(
                request,
                "Interview status updated successfully!"
            )
        else:
            messages.error(request, "Invalid interview status.")

    return redirect("recruiter_interviews")