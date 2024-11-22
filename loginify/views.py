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
from .serializer import UserSerializer


def login_user(request):
    # Initialize context
    context = {}
    
    if 'username' in request.session:
        print("Already",request.session['username'])
        try:
            user = UserDetail.objects.get(username=request.session['username'])
            serializer = UserSerializer(user)
            context = serializer.data
    
        except UserDetail.DoesNotExist:
            del request.session['username']

    if request.method == 'POST':
        print('POST')
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = UserDetail.objects.get(email=email)

            if password == user.password:
                request.session['username'] = user.username
                request.session.set_expiry(20) 
                serializer = UserSerializer(user)
                context = serializer.data
                messages.success(request, 'Login Successfully!')
                return redirect('home')
            
            else:
                messages.error(request, 'User credentials are not valid!')
        
        except UserDetail.DoesNotExist:
            messages.error(request, 'No user found with this email')
    
    print(context)
    return render(request, 'index.html', context)

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


# request.session.flush() completely deletes the session from the database and cookie
# request.session.clear() removes all session data but keeps the session key
def logout_user(request):
    # logout(request)
    request.session.flush()
    messages.success(request,"Logout successfully!!")
    return redirect('home')

def profile(request):
    if 'username' not in request.session:
        messages.error(request,'Please Login First!!')
        return redirect('home')
    
    try:
        user = UserDetail.objects.get(username=request.session['username'])
    except Exception as e:
        messages.error(request,str(e))
        return redirect('home')

    if request.method == 'POST':
        data = request.POST  
        username = data['username']
        email = data['email']
        
        try:
            if username:
                user.username = username
                request.session['username'] = username
            if email:
                user.email = email
        
            user.save()
            
            messages.success(request,'User updated successfully')
        
        except Exception as e:
            messages.error(request,str(e))
            return redirect('profile')
        
    serializer = UserSerializer(user)
    context = serializer.data
  
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
