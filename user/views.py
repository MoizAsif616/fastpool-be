from django.shortcuts import render
from rest_framework import viewsets, status
from .models import *
from .serializers import *
from utils.supabase_client import supabase
from rest_framework.response import Response
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from utils.helper import*
from django.core.cache import cache
import uuid
# Create your views here.

import logging
logger = logging.getLogger(__name__)

from django.views import View

class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer

  def create(self, request, *args, **kwargs):
    # throw error: User creation only via /signup/
    raise MethodNotAllowed('POST', detail='User can only be created via /signup/')
  
  @action(detail=False, methods=['post'], url_path='signup')
  def signup(self, request):
    serializer = self.get_serializer(data=request.data)
    if serializer.is_valid():
      send_verification_email(request.data.get('username'), request.data.get('email'))
      return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_400_BAD_REQUEST)
  
    

  @action(detail=False, methods=['post'], url_path='login')
  def login(self, request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
      return Response({'error': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
      # Authenticate user with Supabase Auth
      response = supabase.auth.sign_in_with_password({'email': email, 'password': password})
      user = User.objects.get(email=email)
      access_token = response.session.access_token
      refresh_token = response.session.refresh_token

      return Response({
        'user_id': user.id,
        'access_token': access_token,
        'refresh_token': refresh_token
      }, status=status.HTTP_200_OK)
    
    except Exception as e:
      return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    
  @action(detail=False, methods=['post'], url_path='verify')
  def verify(self, request):
    data = request.data
    otp = data.pop('otp', None)
    if otp:
      cache_key = f'otp_{data.get("email")}'
      if cache.get(cache_key) == otp:
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
          user = serializer.save()  # Calls `create()` in `UserSerializer`
          return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'error': 'OTP is required'}, status=status.HTTP_400_BAD_REQUEST)
  
 # this is resend otp route if the otp has been expired
  @action(detail=False, methods=['post'], url_path='resend-otp')
  def resend_otp(self, request):
    email = request.data.get('email')
    resend_verification_email(email)
    return Response(status=status.HTTP_200_OK)

  @action(detail=False, methods=['post'], url_path='request-link')
  def send_password_reset_link(self, request):
    email = request.data.get('email')
    url = request.data.get('url')
    if not email:
      return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
      user = User.objects.get(email=email)
      if user:
        token = uuid.uuid4().hex
        cache.set(token, user.email, timeout=5*3600)
        print("making url")
        URL = url + '?token=' + token
        send_password_reset_email(email, URL)
        return Response(status=status.HTTP_200_OK)
      else:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
      return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
  @action(detail=False, methods=['post'], url_path='reset')
  def reset_password(self, request):
    token = request.data.get('token')
    password = request.data.get('password')
    if not token:
      return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
    if not password:
      return Response({'error': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)
    try:
      email = cache.get(token)
      if email:
        sid = get_auth_id(email)
        print("sid is",sid)
        print("email is",email)
        if sid:
          try:
            supabase.auth.admin.delete_user(sid)
          except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
          
          supabase.auth.sign_up({'email': email, 'password':password})
        else:
          return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
      else:
        return Response({'error': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)
      
      return Response(status=status.HTTP_200_OK)
    except Exception as e:
      return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
  def destroy(self, request, *args, **kwargs):
    user = self.get_object()  # Get the User instance being deleted

    if hasattr(user, 'rider'):
      user.rider.delete()  # Directly delete the Rider instance

    if hasattr(user, 'driver'):
      user.driver.delete()  # Directly delete the Driver instance

    sid = get_auth_id(user.email)
    if sid:
      supabase.auth.admin.delete_user(sid)

    user.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)