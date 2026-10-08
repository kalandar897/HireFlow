from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from accounts.decorators import role_required
from django.contrib import messages
from .forms import RegisterForm
from django.core.exceptions import PermissionDenied
from .models import CandidateProfile
from .forms import CandidateProfileForm

# Create your views here.

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect("dashboard")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(
                request,
                "Invalid username or password. Please try again."
            )
    else:
        form = AuthenticationForm(request)

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    if request.method == "POST":
        logout(request)
        return redirect("login")

    return redirect("dashboard")


@login_required
def dashboard_view(request):
    if request.user.role == "ADMIN" or request.user.is_superuser:
        return redirect("admin_dashboard")

    if request.user.role == "RECRUITER":
        return redirect("recruiter_dashboard")

    if request.user.role == "CANDIDATE":
        return redirect("candidate_dashboard")

    raise PermissionDenied


@role_required("CANDIDATE")
def candidate_profile(request):

    profile, created = CandidateProfile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":
        form = CandidateProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():
            form.save()
            return redirect("candidate_profile")
    else:
        form = CandidateProfileForm(instance=profile)

    return render(
        request,
        "accounts/candidate_profile.html",
        {"form": form, "profile": profile}
    )