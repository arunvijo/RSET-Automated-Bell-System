from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from datetime import datetime

@csrf_protect
def login_user(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/home/')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/home/')
        else:
            return render(request, 'login.html', {'obj': 'Invalid username or password'})
    
    return render(request, 'login.html', {})

@csrf_protect
def home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html', {'username': str(request.user.username)})
    else:
        return render(request, 'login.html', {'obj': 'Please login first'})

def logout_user(request):
    logout(request)
    return render(request, 'login.html', {'obj': 'Logged out successfully'})

@csrf_protect
def apply(request):
    currentvalues = {}
    currentvalues["main"] = main_current.objects.get(id=1).name
    currentvalues["pg"] = pg_current.objects.get(id=1).name
    currentvalues["ke"] = ke_current.objects.get(id=1).name
    
    if request.method == 'POST':
        if request.user.is_authenticated:
            main_str = request.POST.get('main')
            pg_str = request.POST.get('pg')
            ke_str = request.POST.get('ke')
            obj1 = main_current.objects.get(id=1)
            obj2 = pg_current.objects.get(id=1)
            obj3 = ke_current.objects.get(id=1)
            if main_str:
                obj1.name = main_str
                obj1.save()
                currentvalues["main"] = main_str
            if pg_str:
                obj2.name = pg_str
                obj2.save()
                currentvalues["pg"] = pg_str
            if ke_str:
                obj3.name = ke_str
                obj3.save()
                currentvalues["ke"] = ke_str
            
            obj = blk.objects.all()
            return render(request, 'apply.html', {'obj': obj, 'status': 'Successfully applied', 'username': str(request.user.username), 'currvals': currentvalues, 'count': range(1, 29)})
        else:
            return render(request, 'login.html', {'obj': 'Please login first'})
    
    if request.user.is_authenticated:
        obj = blk.objects.all()
        return render(request, 'apply.html', {'obj': obj, 'username': str(request.user.username), 'currvals': currentvalues})
    else:
        return render(request, 'login.html', {'obj': 'Please login first'})

@csrf_protect
def create(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data_dict = {'name': request.POST.get('name')}
            for x in range(1, 29):
                data_dict['b' + str(x)] = request.POST.get('b' + str(x)) if request.POST.get('b' + str(x)) else None
                data_dict['t' + str(x)] = request.POST.get('t' + str(x)) if request.POST.get('t' + str(x)) else None
                data_dict['a' + str(x)] = request.POST.get('a' + str(x)) if request.POST.get('a' + str(x)) else False
                for y in range(7):
                    data_dict['b' + str(x) + '_d' + str(y)] = request.POST.get('b' + str(x) + '_d' + str(y)) if request.POST.get('b' + str(x) + '_d' + str(y)) else False
            obj = blk(**data_dict)
            try:
                obj.save()
                return HttpResponseRedirect('/home')
            except Exception as e:
                return render(request, 'create.html', {'obj': 'Error occurred, Please Try again', 'username': str(request.user.username)})
        else:
            return render(request, 'login.html', {'obj': 'Please login first'})
    
    if request.user.is_authenticated:
        return render(request, 'create.html', {'obj': 'Create new profile', 'username': str(request.user.username), 'count': range(1, 29)})
    else:
        return render(request, 'login.html', {'obj': 'Please login first'})
