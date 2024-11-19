from django.contrib import admin
from .models import UserDetail
# Register your models here.

@admin.register(UserDetail)
class User(admin.ModelAdmin):
    list_display = ('id','username','email','password')