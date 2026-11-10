import json
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core import serializers
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from accounts.models import Profile
from jobs.models import Job


class Command(BaseCommand):
    help = "Import the original CareerConnect jobs and recruiter ownership."

    @transaction.atomic
    def handle(self, *args, **options):
        file_path = Path(settings.BASE_DIR) / "jobs_data.json"

        if not file_path.exists():
            raise CommandError("jobs_data.json file not found.")

        try:
            raw_data = file_path.read_text(encoding="utf-8-sig")
            records = json.loads(raw_data)
        except (OSError, json.JSONDecodeError) as error:
            raise CommandError(f"Could not read jobs_data.json: {error}")

        User = get_user_model()
        usernames = set()

        for record in records:
            recruiter = record.get("fields", {}).get("recruiter")
            if not isinstance(recruiter, list) or len(recruiter) != 1:
                raise CommandError("Invalid recruiter reference in jobs_data.json.")
            usernames.add(recruiter[0])

        created_users = 0

        for username in sorted(usernames):
            user, created = User.objects.get_or_create(username=username)

            if created:
                user.set_unusable_password()
                user.save(update_fields=["password"])
                created_users += 1

            Profile.objects.get_or_create(
                user=user,
                defaults={"role": "recruiter"}
            )

        imported = 0
        skipped = 0

        try:
            for item in serializers.deserialize(
                "json", raw_data, ignorenonexistent=True
            ):
                job = item.object

                exists = Job.objects.filter(
                    recruiter=job.recruiter,
                    title=job.title,
                    company=job.company,
                    location=job.location,
                    description=job.description,
                ).exists()

                if exists:
                    skipped += 1
                    continue

                item.save()
                imported += 1

        except Exception as error:
            raise CommandError(f"Job import failed: {error}")

        self.stdout.write(self.style.SUCCESS(
            f"Import complete: {imported} jobs imported, "
            f"{skipped} already existed, "
            f"{created_users} recruiter user records created."
        ))
