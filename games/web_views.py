from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from rest_framework.authtoken.models import Token

from .models import ApiUserProfile, Game


def landing_page_view(request):
    """Modern public landing page introducing the Game API with docs and demo."""
    sample_games = Game.objects.filter(is_active=True)[:5]
    total_games = Game.objects.filter(is_active=True).count()
    return render(request, 'index.html', {
        'sample_games': sample_games,
        'total_games': total_games,
    })


def signup_view(request):
    """User registration page for developer accounts."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, 'signup.html', {'username': username, 'email': email})

        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'signup.html', {'username': username, 'email': email})

        if len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
            return render(request, 'signup.html', {'username': username, 'email': email})

        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username already taken. Please choose another.")
            return render(request, 'signup.html', {'username': username, 'email': email})

        if email and User.objects.filter(email__iexact=email).exists():
            messages.error(request, "An account with this email already exists.")
            return render(request, 'signup.html', {'username': username, 'email': email})

        # Create user (signal will auto-generate Token and ApiUserProfile)
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, f"Welcome to Game API, {user.username}! Your API token is ready.")
        return redirect('dashboard')

    return render(request, 'signup.html')


def login_view(request):
    """Developer login page."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active:
                messages.error(request, "Your account is inactive. Please contact support.")
                return render(request, 'login.html', {'username': username})

            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, 'login.html', {'username': username})

    return render(request, 'login.html')


def logout_view(request):
    """Log out and redirect to landing page."""
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('landing-page')


@login_required
def dashboard_view(request):
    """Developer console showing API key, quota, and interactive playground."""
    token, _ = Token.objects.get_or_create(user=request.user)
    profile, _ = ApiUserProfile.objects.get_or_create(user=request.user)
    sample_games = Game.objects.filter(is_active=True)[:10]

    return render(request, 'dashboard.html', {
        'token': token.key,
        'profile': profile,
        'sample_games': sample_games,
    })
