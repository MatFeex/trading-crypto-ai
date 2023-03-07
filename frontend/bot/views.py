from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import UserFormCustom
from .models import User



# Create your views here.

def home(request):
    return render(request,'home.html')

def register_user(request): 

    if request.method == 'POST':
          
        user = User.objects.create(
            username = request.POST['username'],
            password= request.POST['password'],
            email=request.POST['email'],
            api_key=request.POST['key'],
            api_secret=request.POST['secret'],
            cash=request.POST['cash'],
        )
        user.set_password(request.POST['password'])
        login(request,user)
        return redirect('trades')
    
    return render(request,'register.html')



def login_user(request):

    # if request.user.is_authenticated : return redirect('trades')

    if request.method == 'POST' :
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user != None :
            login(request, user)
            # return redirect('trades')
        else : return redirect('home')
    return render(request,'login.html')