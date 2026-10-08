from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ("CANDIDATE", "Candidate"),
        ("RECRUITER", "Recruiter"),
        ("ADMIN", "Admin"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="CANDIDATE"
    )

    def __str__(self):
        return self.username
    

class CandidateProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="candidate_profile"
    )

    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    education = models.CharField(max_length=200, blank=True)
    skills = models.TextField(blank=True)
    experience = models.CharField(max_length=100, blank=True)
    resume = models.FileField(
        upload_to="candidate_resumes/",
        blank=True,
        null=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name or self.user.username}'s Profile"