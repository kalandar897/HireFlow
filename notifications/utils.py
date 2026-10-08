from .models import Notification

def create_notification(recipient, message):
    Notification.objects.create(
        recipient=recipient,
        message=message
    )