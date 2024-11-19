from sqlite3 import IntegrityError
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
import json
from django.forms.models import model_to_dict

from .models import UserDetail

current_user = {}
# Create your views here.
@csrf_exempt
def login_user(request):
    global current_user
    
    context = {}
    if current_user:
        context['username'] = current_user.username

    print("context",context)

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = UserDetail.objects.get(email=email)

            if password == user.password:
                messages.success(request,'Login Successfully!')
                
                current_user = user
                context['username'] = user.username
                print(user.username,context)

            else:
                messages.error(request,'User credentials is not valid!')
        
        except UserDetail.DoesNotExist:
            messages.error(request, 'No user found with this email')
            
        # return redirect('home')
    return render(request,'index.html',context)

def register_user(request):
    if request.method=='POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = UserDetail.objects.create(username=username,email=email,password=password)
            user.save()
            messages.success(request,"Register Successfully, Login now")
            return redirect('home')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('register')
        
    return render(request,'register_form.html')

def logout_user(request):
    logout(request)
    global current_user
    current_user = {}
    print(current_user)
    messages.success(request,"Logout successfully!!")
    print("About to redirect")
    return redirect('home')

def profile(request):
    context = {}
    try:
        user = current_user 
        print("profile",user) 
        context['username'] = user.username
        context['email'] = user.email
    except Exception as e:
        messages.error(request,'Please login first')
        return redirect('home')

    if request.method == 'POST':
        data = request.POST  
        
        username = data['username']
        email = data['email']
        
        try:
            if username:
                user.username = username
            if email:
                user.email = email
        
            user.save()
            context['username'] = username 
            context['email'] = email
            messages.success(request,'User updated successfully')
            return render(request, 'profile.html', context)
        
        except Exception as e:
            messages.error(request,str(e))
            return redirect('profile')

    return render(request,'profile.html', context)

# get all the users
def get_users(request):
    users = UserDetail.objects.all()
    users_serialized = serialize('json', users)
    users_json = json.loads(users_serialized)
    return JsonResponse(users_json,safe=False)

# get user by id
def get_user(request,id):
    user = UserDetail.objects.get(id=id)
    print((user.email))
    user_dict = model_to_dict(user)
    return JsonResponse(user_dict)

# get user by id and delete it
def delete_user(request,id):
    try:
        if id:
            user = UserDetail.objects.get(id=id)
            user.delete()
            return JsonResponse({"message":'User deleted successfully'})
    except User.DoesNotExist:
        return JsonResponse({"message": "User does not exist"}, status=404)
