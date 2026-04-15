import random
import time

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from books.models import Book
from circulation.models import BorrowTransaction as BorrowRecord
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

    if request.user.is_superuser or profile.role in ['admin', 'librarian']:
        return redirect('accounts:admin_dashboard')

    return redirect('accounts:user_dashboard')


@login_required
def admin_dashboard(request):

    profile, _ = StaffProfile.objects.get_or_create(user=request.user)

    # ROLE CHECK
    if not (request.user.is_superuser or profile.is_manager):
        return redirect('accounts:user_dashboard')

    total_users = User.objects.filter(
        is_staff=False,
        is_superuser=False
    ).count()

    total_books = Book.objects.count()

    total_borrowed = BorrowRecord.objects.filter(status='borrowed').count()
    total_returned = BorrowRecord.objects.filter(status='returned').count()

    overdue = BorrowRecord.objects.filter(
        status='borrowed',
        due_date__lt=timezone.now()
    ).count()

    overdue_records = BorrowRecord.objects.filter(
        status='borrowed',
        due_date__lt=timezone.now()
    )

    return render(request, 'admin_dashboard.html', {
        'total_users': total_users,
        'total_books': total_books,
        'total_borrowed': total_borrowed,
        'total_returned': total_returned,
        'overdue': overdue,
        'overdue_records': overdue_records,
        'is_manager': profile.role == 'librarian',
        'is_superuser': request.user.is_superuser,
    })


@login_required
def user_dashboard(request):
    profile, _ = StaffProfile.objects.get_or_create(user=request.user)
    return render(request, 'user_dashboard.html', {'profile': profile})

def logout_view(request):
    logout(request)
    return redirect('accounts:login')


# ================= SEND OTP =================
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get('email')

        user = User.objects.filter(email=email).first()

        if not user:
            return render(request, 'forgot_password.html', {
                'error': 'Email not found'
            })

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

    return render(request, 'forgot_password.html')


# ================= VERIFY OTP =================
def verify_otp(request):
    error = None

    session_otp = request.session.get('otp')
    otp_time = request.session.get('otp_time')

    if not session_otp or not otp_time:
        return redirect('accounts:forgot_password')

    if request.method == "POST":
        user_otp = request.POST.get('otp')

        # expired check (60s)
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

    user = User.objects.filter(email=email).first()
    if not user:
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

    user = User.objects.filter(email=email).first()

    if not user:
        return redirect('accounts:login')

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

        if User.objects.filter(email=email).exists():
            return render(request, 'sign_up.html', {
                'error': 'Email already exists'
            })

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1
        )

        return redirect('accounts:login')

    return render(request, 'sign_up.html')

@login_required
def member_list(request):

    users = User.objects.filter(
        is_staff=False,
        is_superuser=False
    ).prefetch_related('staffprofile')

    return render(request, 'user_management.html', {
        'users': users
    })
@login_required
def member_create(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        phone = request.POST.get('phone')
        occupation = request.POST.get('occupation')
        role = request.POST.get('role')
        points = request.POST.get('points') or 0

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        StaffProfile.objects.create(
            user=user,
            phone=phone,
            occupation=occupation,
            role=role,
            points=points
        )

    return redirect('accounts:member_list')

@login_required
def member_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile, _ = StaffProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        user.save()

        profile.phone = request.POST.get('phone')
        profile.occupation = request.POST.get('occupation')
        profile.role = request.POST.get('role')
        profile.points = request.POST.get('points') or 0
        profile.save()

    return redirect('accounts:member_list')

@login_required
@login_required
def member_delete(request, pk):
    user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        user.delete()

    return redirect('accounts:member_list')

@login_required
def member_json(request, pk):
    user = get_object_or_404(User.objects.select_related('staffprofile'), pk=pk)

    profile = getattr(user, 'staffprofile', None)

    return JsonResponse({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "phone": profile.phone if profile else "",
        "occupation": profile.occupation if profile else "",
        "role": profile.role if profile else "user",
        "points": profile.points if profile else 0,
    })