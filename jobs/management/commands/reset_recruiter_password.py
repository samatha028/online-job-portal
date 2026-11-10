import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Safely reset a recruiter's password using an environment variable."

    def handle(self, *args, **options):
        password = os.environ.get("CAREERCONNECT_RESET_PASSWORD")

        if not password:
            self.stdout.write("Password reset skipped: no reset password configured.")
            return

        username = os.environ.get("CAREERCONNECT_RESET_USERNAME", "rahul")
        User = get_user_model()

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stderr.write(f"Recruiter account '{username}' not found.")
            return

        user.set_password(password)
        user.save(update_fields=["password"])

        self.stdout.write(self.style.SUCCESS(
            f"Password successfully updated for {username}."
        ))
