import random
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from django.core.cache import cache
from .templates import *
# Create your models here.
def generate_Otp():
    return random.randint(100000, 999999)

def send_verification_email(username, email):
    otp = generate_Otp()
    cache_key = f'otp_{email}'
    cache.set(cache_key, otp, timeout=120) # 2 minutes
    subject = 'Welcome to Fastpool'
    html_message = render_to_string('welcome_email.html', {'user': username, 'otp': otp})
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    to = email

    send_mail(subject, plain_message, from_email, [to], html_message=html_message)
    
def Resend_verification_email(email):
    otp = generate_Otp()
    cache_key = f'otp_{email}'
    cache.set(cache_key, otp, timeout=120) # 2 minutes
    subject = 'Resend OTP'
    html_message = render_to_string('resend_email.html', {'otp': otp})
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    to = email

    send_mail(subject, plain_message, from_email, [to], html_message=html_message)    