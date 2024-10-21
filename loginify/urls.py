from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_user,name='home'),
    path('register/',views.register_user,name='register'),
    path('logout/',views.logout_user,name='logout'),
    path('users/',views.get_users,name='users'),
    path('profile/',views.profile,name='profile'),
    path('user/<int:id>/',views.get_user,name='user_details'),
    path('user/delete/<int:id>/',views.delete_user,name='user_delete')
]
