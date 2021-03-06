from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import Todo, Quote
from django.utils import timezone
from django.db.models.aggregates import Count
from django.contrib.auth.decorators import login_required
from random import randint

def home(request) :
    count = Quote.objects.all().aggregate(count=Count('id'))['count']
    rand_index = randint(0, count - 1)
    time_quote = Quote.objects.all()[rand_index]
    
    response = render(request, 'todo/home.html', {'time_quote':time_quote})
    if(request.COOKIES.get('theme', '') == ''):
        response.set_cookie('theme', 'light')
    return response

def signupuser(request) :
    if request.method == 'GET' :
        return render(request, 'todo/signupuser.html', {'form':UserCreationForm()})

    else :
        if request.POST['password1'] == request.POST['password2'] :
            try :
                user = User.objects.create_user(request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('home')

            except IntegrityError :
                return render(request, 'todo/signupuser.html', {'form':UserCreationForm(), 'error':'Username already taken!'})    

        else :
            return render(request, 'todo/signupuser.html', {'form':UserCreationForm(), 'error':'Passwords did not match!'})

def loginuser(request) :
    if request.method == 'GET' :
        return render(request, 'todo/loginuser.html', {'form':AuthenticationForm()})

    else :
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None :
            return render(request, 'todo/loginuser.html', {'form':AuthenticationForm(), 'error':'Username and password do not match!'})
        else :
            login(request, user)
            return redirect('home')

@login_required
def logoutuser(request) :
    if request.method == 'POST' :
        logout(request)
        return redirect('home')

@login_required
def createtodo(request) :
    if request.method == 'GET' :
        return render(request, 'todo/createtodo.html', {'form':TodoForm()})
    else :
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            response = redirect('currenttodos')
            response.set_cookie('origin', 'create')
            return response
        except ValueError :
            return render(request, 'todo/createtodo.html', {'form':TodoForm(), 'error':'Bad data passed. Please try again!'})

@login_required
def currenttodos(request) :
    if request.COOKIES.get('origin', '') == 'create' :
        message = 'Task created!'
    elif request.COOKIES.get('origin', '') == 'update' :
        message = 'Task updated!'
    elif request.COOKIES.get('origin', '') == 'delete' :
        message = 'Task deleted!'
    elif request.COOKIES.get('origin', '') == 'complete' :
        message = 'Task marked complete!'
    elif request.COOKIES.get('origin', '') == 'undocomplete' :
        message = 'Task marked incomplete!'
    else :
        message = ''
    
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    count = Quote.objects.all().aggregate(count=Count('id'))['count']
    rand_index = randint(0, count - 1)
    time_quote = Quote.objects.all()[rand_index]

    response = render(request, 'todo/currenttodos.html', {'todos':todos, 'time_quote':time_quote, 'message':message})
    response.delete_cookie('origin')
    return response

@login_required
def completedtodos(request) :
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'todo/completedtodos.html', {'todos':todos})

@login_required
def viewtodo(request, todo_pk) :
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)

    if request.method == 'GET' :
        form = TodoForm(instance=todo)
        return render(request, 'todo/viewtodo.html', {'todo':todo, 'form':form})
    else :
        try :
            form = TodoForm(request.POST, instance=todo)
            form.save()
            response = redirect('currenttodos')
            response.set_cookie('origin', 'update')
            return response
        except ValueError :
            return render(request, 'todo/viewtodo.html', {'todo':todo, 'form':form, 'error':'Bad data passed. Please try again!'})

@login_required
def completetodo(request, todo_pk) :
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)

    if request.method == 'POST' :
        todo.datecompleted = timezone.now()
        todo.save()
        response = redirect('currenttodos')
        response.set_cookie('origin', 'complete')
        return response

@login_required
def deletetodo(request, todo_pk) :
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)

    if request.method == 'POST' :
        todo.delete()
        response = redirect('currenttodos')
        response.set_cookie('origin', 'delete')
        return response

@login_required
def undocompletetodo(request, todo_pk) :
    todo = get_object_or_404(Todo, pk=todo_pk, user=request.user)

    if request.method == 'POST' :
        todo.datecompleted = None
        todo.save()
        response = redirect('currenttodos')
        response.set_cookie('origin', 'undocomplete')
        return response
