from django.db import models
from utils.supabase_client import supabase
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
# Create your models here.

class User(models.Model):
  username = models.CharField(max_length=100, blank=False, null=False)
  email = models.EmailField(max_length=100, blank=False, null=False, unique=True) 
  gender = models.CharField(max_length=6, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], default='Male')
  phone = models.CharField(max_length=11, blank=False, null=False)

  class Meta:
    db_table = 'user'

  def __str__(self):
    return self.username
  

class UserProfile(models.Model):
  id = models.OneToOneField(User,primary_key=True, on_delete=models.CASCADE)
  url = models.CharField(max_length=500, blank=True, null=True)
  
  class Meta:
    db_table = 'user_profile'
  def __str__(self):
      return f"{self.user.username}'s profile"


  