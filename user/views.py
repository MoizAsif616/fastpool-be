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
import os
from supabase import create_client, Client
# Create your views here.

import logging
logger = logging.getLogger(__name__)
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
    if not email:
      return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
    Resend_verification_email(email)
    return Response(status=status.HTTP_200_OK)


  @action(detail=False, methods=['post'], url_path='forgot-password')
  def forgot_password(self, request):
      email = request.data.get('email')
      if not email:
          return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

      try:
          # Send a password reset link to the user's email
          response = supabase.auth.reset_password_for_email(email)
          logger.info(f"Supabase response: {response}")
          
          # Check if the request was successful
          if response and response.get('error'):
              return Response({'error': response['error']['message']}, status=status.HTTP_400_BAD_REQUEST)
          
          return Response({'message': 'Password reset link sent to your email'}, status=status.HTTP_200_OK)
      
      except Exception as e:
          logger.error(f"Error in forgot_password: {str(e)}")
          return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
  
  @action(detail=False, methods=['post'], url_path='update-password')
  def update_password(self, request):
        data = request.data
        new_password = data.get('new_password')
      
        if not new_password :
            return Response({'error': 'New password and confirm password are required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Get the access token and refresh token from the Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return Response({'error': 'Invalid or missing access token'}, status=status.HTTP_401_UNAUTHORIZED)

            # Extract the access token and refresh token from the header
            tokens = auth_header.split(' ')
            if len(tokens) != 3:
                return Response({'error': 'Invalid token format. Expected: Bearer <access_token> <refresh_token>'}, status=status.HTTP_400_BAD_REQUEST)

            access_token = tokens[1]
            refresh_token = tokens[2]

            # Set the access token and refresh token in the Supabase client
            supabase.auth.set_session(access_token, refresh_token)

            # Use Supabase's API to update the password
            response = supabase.auth.update_user({'password': new_password})
            
            if response.get('error'):
                return Response({'error': response['error']['message']}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)