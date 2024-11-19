from django.db import models

# Create your models here.
class UserDetail(models.Model):
    username = models.CharField(max_length=50,unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=12)

    def __str__(self):
        return (f'{self.username}')