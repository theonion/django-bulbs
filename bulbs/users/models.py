from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class User(AbstractBaseUser):
    username = models.CharField(max_length=40, unique=True, db_index=True)
    USERNAME_FIELD = 'username'
