from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def user_login(request):
    if not request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'account/login.html')
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Wrong username or password')
                return redirect('account:login')
    else:
        messages.error(request, 'You are already logged in!')
        return redirect('home')
        # return render(request, 'route/index.html', {'account_message': 'You are already logged in!'})


# @login_required(login_url='account:login')
def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        return render(request, 'account/logout.html')
    else:
        messages.error(request, 'You are already logged out!')
        return redirect('account:login')
        # return render(request, 'route/index.html', {'account_message': 'You are already logged out!'})


def user_registration(request):
    if not request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'account/registration.html')
        if request.method == 'POST':
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            user = User.objects.create_user(username=username or None, email=email or None, password=password or None)
            user.save()
            messages.success(request, 'Your account was created')
            return redirect('account:login')
    else:
        messages.error(request, 'Your account is already created!')
        return redirect('home')
        # return render(request, 'route/index.html', {'account_message': 'Your account is already created!'})
