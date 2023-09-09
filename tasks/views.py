from django.shortcuts import redirect, render, get_object_or_404
# importaciones de librerias para Login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
# crear cookies
from django.contrib.auth import login, logout, authenticate
# error de integridad de datos
from django.db import IntegrityError
#importar formularios
from .forms import *
#importar modelos
from .models import *
#importar django utils para el tiempo
from django.utils import timezone
#proteger rutas
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html', {})


def signUp(request):
    form = UserCreationForm
    if request.method == 'GET':
        return render(request, 'signup.html', {'form': form})
    else:
        if request.POST['password1'] == request.POST['password2']:
            # registrar usuario
            try:
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
            except IntegrityError:
                return render(request,'signup.html', {
                    'form': form,
                    'error': 'User already exist'
                })
        return render(request,'signup.html', {
                    'form': form,
                    'error': 'Password do not match'
                })

@login_required
def tasks(request):
    #mostrar solo las tareas del usuario que necesito
    tasks = Task.objects.filter(user=request.user, date_completed__isnull=True)
    return render(request, 'tasks.html', {
        'tasks': tasks
    })

@login_required
def tasks_completed(request):
    #mostrar solo las tareas del usuario que necesito
    tasks = Task.objects.filter(user=request.user, date_completed__isnull=False).order_by('date_completed')
    return render(request, 'tasks.html', {
        'tasks': tasks
    })

@login_required
def signOut(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'] )
        if user is None:
            return render(request, 'signin.html', {
            'form': AuthenticationForm,
            'error': 'Username or password incorrect'
        })
        else:
            login(request, user)
            return redirect('tasks')
        
@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request,'create_task.html', {
            'form': TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            print(request.POST)
            return redirect ('tasks')
        except ValueError:
            return render(request,'create_task.html', {
            'form': TaskForm,
            'error': 'Please provide valid data'
        })

@login_required         
def task_detail(request,task_id):
    #para que el servidor no se caiga al buscar un id que no tenemos
    #la mejor solución es esta     pk=primarykey
    if request.method == 'GET':
        task = get_object_or_404(Task ,pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render (request,'task_detail.html',{
            'task': task,
            'form': form
        })
    else:
        #print(request.POST) imprimir los datos que llegan por POST
        try:
            task = get_object_or_404(Task ,pk=task_id, user=request.user)
            #validamos que el usuario solo pueda editar sus tareas
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect ('tasks')
        except ValueError:
            return render (request,'task_detail.html',{
            'task': task,
            'form': form,
            'error': "Error updating task"
        })
    
@login_required
def task_complete(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.date_completed = timezone.now()
        task.save()
        return redirect ('tasks')

@login_required
def task_delete(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect ('tasks')