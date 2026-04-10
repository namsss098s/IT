import random
import time

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

import random
import time

from .models import StaffProfile


# ================= LOGIN =================
def login_view(request):
    if request.user.is_authenticated:
        return redirect_dashboard(request)

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            StaffProfile.objects.get_or_create(user=user)
            return redirect_dashboard(request)

        return render(request, 'login.html', {
            'error': 'Invalid username or password'
        })

    return render(request, 'login.html')


def redirect_dashboard(request):
    profile, _ = StaffProfile.objects.get_or_create(user=request.user)

    if request.user.is_superuser or profile.is_manager:
        return redirect('accounts:admin_dashboard')

    return redirect('accounts:user_dashboard')


@login_required
def admin_dashboard(request):
    profile = request.user.staffprofile

    if not (request.user.is_superuser or profile.is_manager):
        return redirect('accounts:user_dashboard')

    return render(request, 'admin_dashboard.html', {'profile': profile})


@login_required
def user_dashboard(request):
    profile = request.user.staffprofile
    return render(request, 'user_dashboard.html', {'profile': profile})


def logout_view(request):
    logout(request)
    return redirect('accounts:login')


# ================= SEND OTP =================
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)

            otp = str(random.randint(100000, 999999))

            request.session['reset_email'] = email
            request.session['otp'] = otp
            request.session['otp_time'] = time.time()

            send_mail(
                'Password Reset OTP',
                f'Your OTP code is: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            return redirect('accounts:verify_otp')

        except User.DoesNotExist:
            return render(request, 'forgot_password.html', {
                'error': 'Email not found'
            })

    return render(request, 'forgot_password.html')


# ================= VERIFY OTP =================
def verify_otp(request):
    error = None

    session_otp = request.session.get('otp')
    otp_time = request.session.get('otp_time')

    # nếu chưa có OTP trong session -> quay lại forgot
    if not session_otp or not otp_time:
        return redirect('accounts:forgot_password')

    if request.method == "POST":
        user_otp = request.POST.get('otp')

        # kiểm tra hết hạn 60s
        if time.time() - otp_time > 60:
            error = "OTP expired. Please resend OTP."

        elif user_otp == session_otp:
            return redirect('accounts:reset_password')

        else:
            error = "Invalid OTP"

    return render(request, 'check_otp.html', {'error': error})

# ================= RESEND OTP =================
def resend_otp(request):
    email = request.session.get('reset_email')

    if not email:
        return redirect('accounts:forgot_password')

    otp = str(random.randint(100000, 999999))

    request.session['otp'] = otp
    request.session['otp_time'] = time.time()

    send_mail(
        'Password Reset OTP',
        f'Your new OTP code is: {otp}',
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

    return render(request, 'check_otp.html', {
        'message': 'New OTP sent to your email'
    })


# ================= RESET PASSWORD =================
def reset_password(request):
    email = request.session.get('reset_email')

    if not email:
        return redirect('accounts:login')

    user = User.objects.get(email=email)

    if request.method == "POST":
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return render(request, 'reset_password.html', {
                'error': 'Passwords do not match'
            })

        user.set_password(password1)
        user.save()

        request.session.flush()
        return redirect('accounts:login')

    return render(request, 'reset_password.html')
def signup_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return render(request, 'sign_up.html', {
                'error': 'Passwords do not match'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'sign_up.html', {
                'error': 'Username already exists'
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        return redirect('accounts:login')

    return render(request, 'sign_up.html')