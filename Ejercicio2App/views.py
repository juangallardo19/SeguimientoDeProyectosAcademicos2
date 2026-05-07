from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages


def login_view(request):
    if request.user.is_authenticated:
        return redirect('proyecto-list')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('proyecto-list')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'Ejercicio2App/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def es_docente(user):
    return user.groups.filter(name='docente').exists() or user.is_staff


def es_estudiante(user):
    return user.groups.filter(name='estudiante').exists()