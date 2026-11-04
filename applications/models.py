
from django.db import models
from django.contrib.auth.models import User
from jobs.models import Job


class Application(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('selected', 'Selected'),
        ('not_shortlisted', 'Not Shortlisted'),
        ('rejected', 'Rejected'),
    ]

    job = models.ForeignKey(Job, on_delete=models.CASCADE)

    applicant = models.ForeignKey(User, on_delete=models.CASCADE)

    cover_letter = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    resume_viewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.applicant.username + " - " + self.job.title


class Notification(models.Model):

    NOTIFICATION_TYPES = [
        ('status_update', 'Application Status Update'),
        ('resume_viewed', 'Resume Viewed'),
    ]

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='notifications'
    )

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES
    )

    message = models.TextField()

    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recipient.username} - {self.message}"
