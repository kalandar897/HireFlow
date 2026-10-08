from django.db import models

class Interview(models.Model):

    MEETING_MODES = [
        ("ONLINE", "Online"),
        ("OFFLINE", "Offline"),
    ]

    INTERVIEW_STATUSES = [
        ("SCHEDULED", "Scheduled"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    application = models.ForeignKey(
        "applications.Application",
        on_delete=models.CASCADE,
        related_name="interviews"
    )

    interview_date = models.DateTimeField()

    meeting_mode = models.CharField(
        max_length=10,
        choices=MEETING_MODES,
        default="ONLINE"
    )

    status = models.CharField(
        max_length=15,
        choices=INTERVIEW_STATUSES,
        default="SCHEDULED"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interview - {self.application}"