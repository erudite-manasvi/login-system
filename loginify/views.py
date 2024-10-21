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

# Create your views here.
@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            messages.error(request, 'No user found with this email')
            return redirect('home')

        user = authenticate(request,username=username,password=password)

        if user is not None:
            login(request,user)
            messages.success(request,'You have been Logged In')
            return redirect('home')
        else:
            messages.error(request,'There was an error while Logging In')
            return redirect('home')

    return render(request,'index.html')

def register_user(request):
    if request.method=='POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = User.objects.create_user(username=username,email=email,password=password)
            messages.success(request,"Register Successfully, Login now")
            return redirect('home')
        except Exception as e:
            messages.error(request, str(e))
            return redirect('register')
        
    return render(request,'register_form.html')

def logout_user(request):
    logout(request)
    messages.success(request,"Logout successfully!!")
    print("About to redirect")
    return redirect('home')

def profile(request):
    if request.method == 'POST':
        user = request.user
        data = request.POST  
        
        username = data['username']
        email = data['email']
        
        try:
            if username:
                user.username = username
            if email:
                user.email = email
        
            user.save()

            messages.success(request,'User updated successfully')
        
            return redirect('home')
        
        except Exception as e:
            messages.error(request,str(e))
            return redirect('profile')

    return render(request,'profile.html')

# get all the users
def get_users(request):
    users = User.objects.all()
    users_serialized = serialize('json', users)
    users_json = json.loads(users_serialized)
    return JsonResponse(users_json,safe=False)

# get user by id
def get_user(request,id):
    user = User.objects.get(id=id)
    print((user.email))
    user_dict = model_to_dict(user)
    return JsonResponse(user_dict)

# get user by id and delete it
def delete_user(request,id):
    try:
        if id:
            user = User.objects.get(id=id)
            user.delete()
            return JsonResponse({"message":'User deleted successfully'})
    except User.DoesNotExist:
        return JsonResponse({"message": "User does not exist"}, status=404)
