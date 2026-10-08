from django.db import models
from django.conf import settings

# Create your models here.

class Job(models.Model):
    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=150)
    description = models.TextField()
    location = models.CharField(max_length=150)
    required_skills = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title