from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User


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
                return render(request, 'account/login.html', {'account_message': 'Wrong username or password'})
    else:
        return render(request, 'route/index.html', {'account_message': 'You are already logged in!'})


def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        return render(request, 'account/logout.html')
    else:
        return render(request, 'route/index.html', {'account_message': 'You are already logged out!'})


def user_registration(request):
    if not request.user.is_authenticated:
        if request.method == 'GET':
            return render(request, 'account/registration.html')
        if request.method == 'POST':
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            return redirect('home')
    else:
        return render(request, 'route/index.html', {'account_message': 'Your account is already created!'})
