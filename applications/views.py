
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages

from jobs.models import Job
from .models import Application


@login_required
@require_POST
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    # Only Job Seekers can apply
    profile = getattr(request.user, 'profile', None)

    if profile is None or profile.role != 'job_seeker':
        messages.error(
            request,
            "Only Job Seekers can apply for jobs."
        )
        return redirect('job_detail', id=job.id)

    # Do not allow applying to own job
    if job.recruiter == request.user:
        messages.error(
            request,
            "You cannot apply for your own job."
        )
        return redirect('job_detail', id=job.id)

    application, created = Application.objects.get_or_create(
        job=job,
        applicant=request.user
    )

    if created:
        messages.success(
            request,
            "Successfully applied for this job!"
        )
    else:
        messages.info(
            request,
            "You have already applied for this job."
        )

    return redirect('job_detail', id=job.id)


@login_required
def my_applications(request):
    profile = getattr(request.user, 'profile', None)

    if profile is None or profile.role != 'job_seeker':
        messages.error(
            request,
            "Only Job Seekers can view applications."
        )
        return redirect('job_list')

    applications = Application.objects.filter(
        applicant=request.user
    ).select_related('job').order_by('-applied_at')

    return render(
        request,
        'applications/my_applications.html',
        {'applications': applications}
    )
