import random
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.core.cache import cache
from .templates import *
from rest_framework.response import Response
from rest_framework import status
from .supabase_client import supabase
# Create your models here.
def generate_Otp():
  return str(random.randint(100000, 999999))

def send_verification_email(username, email):
	try:
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