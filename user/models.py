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
  
  def get_auth_id(self):
    # Fetch Supabase Auth ID by comparing emails
    auth_users = supabase.auth.admin.list_users()
    for auth_user in auth_users:
      if auth_user.email == self.email:
        return auth_user.id
    return None
  
  def update_password(self, new_password):
    # Update password in Supabase Auth
    auth_id = self.get_auth_id()
    if auth_id:
      supabase.auth.admin.update_user_by_id(
        uid=auth_id,
        attributes={'password': new_password}
      )
      return True
    return False
  
  def delete_auth_record(self):
    # Delete user from Supabase Auth
    auth_id = self.get_auth_id()
    if auth_id:
      supabase.auth.admin.delete_user(auth_id)
      return True
    return False

  