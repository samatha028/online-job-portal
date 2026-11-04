from django.shortcuts import render
from .models import Job

def job_list(request):
    jobs = Job.objects.all().order_by('-created_at')
    print("TOTAL JOBS:", jobs.count())
    print("JOB DATA:", list(jobs.values('id', 'title')))
    return render(request, 'jobs/job_list.html', {'jobs': jobs})
def job_detail(request, id):
    job = Job.objects.get(id=id)
    return render(request, 'jobs/job_detail.html', {'job': job})