from django.urls import path
from . import views


urlpatterns = [
    path('recruiter-dashboard/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('post-job/', views.post_job, name='post_job'),
    path('edit-job/<int:job_id>/', views.edit_job, name='edit_job'),
    path('delete-job/<int:job_id>/', views.delete_job, name='delete_job'),
    path('job-applications/<int:job_id>/', views.job_applications, name='job_applications'),
    path('update-application-status/<int:application_id>/', views.update_application_status, name='update_application_status'),
    path('job-seeker-notifications/', views.job_seeker_notifications, name='job_seeker_notifications'),
    path('mark-notification-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
    path(
    'view-applicant-resume/<int:application_id>/',
    views.view_applicant_resume,
    name='view_applicant_resume'
    ),
]