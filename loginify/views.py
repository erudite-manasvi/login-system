from sqlite3 import IntegrityError
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.core.serializers import serialize
import json
from django.forms.models import model_to_dict
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserDetail
from .serializer import UserSerializer
from .forms import UserForm
import jwt
from django.conf import settings

# using session
# def login_user(request):
#     # Initialize context
#     context = {}
    
#     if 'username' in request.session:
#         print("Already",request.session['username'])
#         try:
#             user = UserDetail.objects.get(username=request.session['username'])
#             serializer = UserSerializer(user)
#             context = serializer.data
    
#         except UserDetail.DoesNotExist:
#             del request.session['username']

#     if request.method == 'POST':
#         print('POST')
#         email = request.POST['email']
#         password = request.POST['password']

#         try:
#             user = UserDetail.objects.get(email=email)

#             if password == user.password:
#                 request.session['username'] = user.username
#                 request.session.set_expiry(20) 
#                 serializer = UserSerializer(user)
#                 context = serializer.data
#                 messages.success(request, 'Login Successfully!')
#                 return redirect('home')
            
#             else:
#                 messages.error(request, 'User credentials are not valid!')
        
#         except UserDetail.DoesNotExist:
#             messages.error(request, 'No user found with this email')
    
#     print(context)
#     return render(request, 'index.html', context)

# with JWT
def login_user(request):
    # Check existing token first
    token = request.COOKIES.get('access_token')
    user_data = get_user_from_token(token)
    
    if user_data:
        return render(request, 'index.html', {'user': user_data})

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = UserDetail.objects.get(email=email)
            if password==user.password:  # Use proper password hashing
                serializer = UserSerializer(user)
                user_data = serializer.data

                refresh = RefreshToken.for_user(user)
                refresh['email'] = user_data['email']
                refresh['username'] = user_data['username']

                response = render(request, 'index.html', {'user': user_data})
                response.set_cookie('access_token', str(refresh.access_token))
                response.set_cookie('refresh_token', str(refresh))
                
                messages.success(request, 'Login successful!')
                return response
            
            messages.error(request, 'Invalid credentials')
        except UserDetail.DoesNotExist:
            messages.error(request, 'User not found')
    
    return render(request, 'index.html', {})


def get_user_from_token(access_token):
    try:
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
        return {
            'username': payload['username'],
            'email': payload['email']
        }
    except:
        return None
    
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
    response = redirect('home')  # or wherever you want to redirect
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    messages.success(request, 'Logged out successfully')
    return response

def profile(request):
    token = request.COOKIES.get('access_token')

    if not token:
        messages.error(request,'Please Login First!!')
        return redirect('home')
    
    user = get_user_from_token(token)
    user_context =  user if user else {}
    
    try:
        user_instance = UserDetail.objects.get(email=user['email'])
    except Exception as e:
        messages.error(request,str(e))
        return redirect('home')

    if request.method == 'POST':
        form = UserForm(request.POST,instance=user_instance)  
        
        if form.is_valid():
            form.save()
            messages.success(request,'User updated successfully')

            refresh = RefreshToken.for_user(user_instance)
            # Add custom claims to token
            refresh['email'] = request.POST['email']
            refresh['username'] = request.POST['username']

            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            response = redirect('profile')
            response.set_cookie('access_token', access_token)
            response.set_cookie('refresh_token', refresh_token)

            return response
        
        else:
            messages.error(request,form.errors)
            return redirect('profile')
        
    if request.method == 'GET':
        form = UserForm(instance=user_instance)
        return render(request, 'profile.html', {'form': form, 'user': user_context})

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
