
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegistrationForm
from .models import Profile
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            Profile.objects.create(
                user=user,
                role=form.cleaned_data['role']
            )

            messages.success(
                request,
                'Registration successful! Please login.'
            )

            return redirect('login')

    else:
        form = RegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form
    })
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'accounts/login.html')
@login_required
def home(request):
    return render(request, 'accounts/home.html')
def user_logout(request):
    logout(request)
    return redirect('login')
@login_required
def upload_resume(request):
    profile = getattr(request.user, 'profile', None)

    if profile is None or profile.role != 'job_seeker':
        messages.error(request, 'Only Job Seekers can upload resumes.')
        return redirect('home')

    if request.method == 'POST':
        resume = request.FILES.get('resume')

        if resume:
            allowed_extensions = ['.pdf', '.doc', '.docx']
            extension = resume.name.lower().rsplit('.', 1)[-1]

            if extension not in ['pdf', 'doc', 'docx']:
                messages.error(request, 'Upload PDF, DOC or DOCX files only.')
            elif resume.size > 5 * 1024 * 1024:
                messages.error(request, 'Resume size must be below 5 MB.')
            else:
                profile.resume = resume
                profile.save(update_fields=['resume'])
                messages.success(request, 'Resume uploaded successfully!')
        else:
            messages.error(request, 'Please select a resume file.')

    return redirect('home')