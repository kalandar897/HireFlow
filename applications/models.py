from django.db import models
from django.conf import settings

# Create your models here.

class Application(models.Model):
    candidate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    job = models.ForeignKey(
        "jobs.Job",
        on_delete=models.CASCADE
    )
    resume = models.FileField(
        upload_to="resumes/",
        blank=True,
        null=True
    )
    cover_letter = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        default="APPLIED"
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate.username} - {self.job.title}"