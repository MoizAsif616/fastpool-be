import random
import os
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.core.cache import cache
from .templates import *
from rest_framework.response import Response
from rest_framework import status
from .supabase_client import supabase
import filetype
# Create your models here.
def generate_Otp():
  return str(random.randint(100000, 999999))

def send_verification_email(username, email):
	try:
		print("Sending email to:", email)
		otp = generate_Otp()
		cache_key = f'otp_{email}'
		cache.set(cache_key, otp, timeout=120) # 2 minutes
		subject = 'Welcome to Fastpool'
		html_message = render_to_string('welcome_email.html', {'user': username, 'otp': otp})
		plain_message = strip_tags(html_message)
		from_email = settings.EMAIL_HOST_USER
		to = email

		send_mail(subject, plain_message, from_email, [to], html_message=html_message)
	except Exception as e:
		print("Error sending email:", e)
		raise e
	
def resend_verification_email(email):
	try:
		if cache.get(f'otp_{email}'): # if previous otp nnot expired yet, delete it
			cache.delete(f'otp_{email}')
		otp = generate_Otp()
		cache_key = f'otp_{email}'
		cache.set(cache_key, otp, timeout=120) # 2 minutes
		subject = 'Resend OTP'
		html_message = render_to_string('resend_otp_email.html', {'otp': otp})
		plain_message = strip_tags(html_message)
		from_email = settings.EMAIL_HOST_USER
		to = email

		send_mail(subject, plain_message, from_email, [to], html_message=html_message) 
	except Exception as e:
		raise e

def send_password_reset_email(email, reset_link):
	try:
		subject = 'Reset Your Password - Fastpool'
		html_message = render_to_string('password_reset_email.html', {'reset_link': "http://" + reset_link})
		plain_message = strip_tags(html_message)
		from_email = settings.EMAIL_HOST_USER
		to = email

		print("url is:","http://" + reset_link)
		send_mail(subject, plain_message, from_email, [to], html_message=html_message)
	except Exception as e:
		raise e
	
def get_auth_id(email):
	# Fetch Supabase Auth ID by comparing emails
	auth_users = supabase.auth.admin.list_users()
	for auth_user in auth_users:
		if auth_user.email == email:
			return auth_user.id
	return None

def upload_picture(user_id, in_memory_file):
    """Uploads or replaces profile picture in Supabase"""
    
    # Read and validate file
    file_bytes = in_memory_file.read()
    kind = filetype.guess(file_bytes)
    if not kind or not kind.mime.startswith('image/'):
        raise ValueError("Only image files allowed")
    
    # Create filename
    file_ext = f".{kind.extension}" if kind.extension else ".jpg"
    filename = f"user_{user_id}/profile{file_ext}"
    
    try:
        # First try to delete existing file if it exists
        supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET).remove([filename])
    except Exception:
        # If file doesn't exist, continue with upload
        pass
    
    # Upload new file
    in_memory_file.seek(0)
    res = supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET).upload(
        file=file_bytes,
        path=filename,
        file_options={"content-type": kind.mime, "upsert": "True"}  # upsert flag
    )
    
    return supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET).get_public_url(filename)