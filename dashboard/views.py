
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from applications.models import Application, Notification
from django.utils import timezone
from jobs.models import Job



def is_recruiter(user):
    profile = getattr(user, 'profile', None)
    return profile is not None and profile.role == 'recruiter'


@login_required
def recruiter_dashboard(request):
    if not is_recruiter(request.user):
        messages.error(request, 'Only recruiters can access this dashboard.')
        return redirect('job_list')

    jobs = Job.objects.filter(
        recruiter=request.user
    ).order_by('-created_at')

    return render(
        request,
        'dashboard/recruiter_dashboard.html',
        {'jobs': jobs}
    )


@login_required
def post_job(request):
    if not is_recruiter(request.user):
        messages.error(request, 'Only recruiters can post jobs.')
        return redirect('job_list')

    if request.method == 'POST':
        title = request.POST.get('title')
        company = request.POST.get('company')
        location = request.POST.get('location')
        description = request.POST.get('description')
        skills_required = request.POST.get('skills_required')
        salary = request.POST.get('salary')
        job_type = request.POST.get('job_type')

        Job.objects.create(
            recruiter=request.user,
            title=title,
            company=company,
            location=location,
            description=description,
            skills_required=skills_required,
            salary=salary,
            job_type=job_type,
        )

        messages.success(request, 'Job posted successfully!')
        return redirect('recruiter_dashboard')

    return render(request, 'dashboard/post_job.html')


@login_required
def edit_job(request, job_id):
    if not is_recruiter(request.user):
        messages.error(request, 'Only recruiters can edit jobs.')
        return redirect('job_list')

    job = get_object_or_404(
        Job,
        id=job_id,
        recruiter=request.user
    )

    if request.method == 'POST':
        job.title = request.POST.get('title')
        job.company = request.POST.get('company')
        job.location = request.POST.get('location')
        job.description = request.POST.get('description')
        job.skills_required = request.POST.get('skills_required')
        job.salary = request.POST.get('salary')
        job.job_type = request.POST.get('job_type')

        job.save()

        messages.success(request, 'Job updated successfully!')
        return redirect('recruiter_dashboard')

    return render(
        request,
        'dashboard/edit_job.html',
        {'job': job}
    )


@login_required
def delete_job(request, job_id):
    if not is_recruiter(request.user):
        messages.error(request, 'Only recruiters can delete jobs.')
        return redirect('job_list')

    job = get_object_or_404(
        Job,
        id=job_id,
        recruiter=request.user
    )

    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully!')
        return redirect('recruiter_dashboard')

    return render(
        request,
        'dashboard/delete_job.html',
        {'job': job}
    )
@login_required
def job_applications(request, job_id):
    if not is_recruiter(request.user):
        messages.error(request, 'Only recruiters can view applications.')
        return redirect('job_list')

    job = get_object_or_404(
        Job,
        id=job_id,
        recruiter=request.user
    )

    applications = Application.objects.filter(
        job=job
    ).select_related('applicant').order_by('-applied_at')

    return render(
        request,
        'dashboard/job_applications.html',
        {
            'job': job,
            'applications': applications
        }
    )


@login_required
@require_POST
def update_application_status(request, application_id):
    if not is_recruiter(request.user):
        messages.error(request, 'Only recruiters can update application status.')
        return redirect('job_list')

    application = get_object_or_404(
        Application,
        id=application_id,
        job__recruiter=request.user
    )

    new_status = request.POST.get('status')
    valid_statuses = dict(Application.STATUS_CHOICES)

    if new_status not in valid_statuses:
        messages.error(request, 'Invalid application status.')
        return redirect('job_applications', job_id=application.job.id)

    if application.status != new_status:
        application.status = new_status
        application.save(update_fields=['status'])

        Notification.objects.create(
            recipient=application.applicant,
            application=application,
            notification_type='status_update',
            message=f"Your application for {application.job.title} has been updated to {valid_statuses[new_status]}."
        )

        messages.success(request, 'Application status updated successfully!')

    return redirect('job_applications', job_id=application.job.id)
@login_required
def job_seeker_notifications(request):
    profile = getattr(request.user, 'profile', None)

    if profile is None or profile.role != 'job_seeker':
        messages.error(request, 'Only Job Seekers can view notifications.')
        return redirect('job_list')

    notifications = Notification.objects.filter(
        recipient=request.user
    ).select_related(
        'application',
        'application__job'
    ).order_by('-created_at')

    return render(
        request,
        'dashboard/job_seeker_notifications.html',
        {
            'notifications': notifications
        }
    )
@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        recipient=request.user
    )

    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=['is_read'])

    return redirect('my_applications')
@login_required
def view_applicant_resume(request, application_id):
    if not is_recruiter(request.user):
        messages.error(request, 'Only recruiters can view resumes.')
        return redirect('job_list')

    application = get_object_or_404(
        Application,
        id=application_id,
        job__recruiter=request.user
    )

    profile = getattr(application.applicant, 'profile', None)

    if profile is None or not profile.resume:
        messages.error(request, 'Applicant has not uploaded a resume.')
        return redirect('job_applications', job_id=application.job.id)

    if application.resume_viewed_at is None:
        application.resume_viewed_at = timezone.now()
        application.save(update_fields=['resume_viewed_at'])

        Notification.objects.create(
            recipient=application.applicant,
            application=application,
            notification_type='resume_viewed',
            message=f'The recruiter viewed your resume for {application.job.title}.'
        )

    return redirect(profile.resume.url)