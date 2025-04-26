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
from utils.decorators import auth_required
from django.core.cache import cache
import uuid
#import messages module to display messages
from django.contrib import messages
# Create your views here.

import logging
logger = logging.getLogger(__name__)

from django.views import View
from driver.models import *
from rider.models import Rider

class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer

  def create(self, request, *args, **kwargs):
    # throw error: User creation only via /signup/
    raise MethodNotAllowed('POST', detail='User can only be created via /signup/')
  
  @action(detail=False, methods=['post'], url_path='signup')
  def signup(self, request):

    serializer = self.get_serializer(data=request.data)
    if serializer.is_valid(raise_exception = True):
      send_verification_email(request.data.get('username'), request.data.get('email'))
      return Response(status=status.HTTP_200_OK)
  
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
  
  
  @action(detail=False, methods=['put'], url_path='profile/edit-profile-picture')
  @auth_required
  def edit_profile_picture(self, request):
    try:
      user = User.objects.get(pk = request.user_id)
    except User.DoesNotExist:
      return Response(
        {'error': 'User not found'},
        status=status.HTTP_404_NOT_FOUND
      )

    ## Check if profile picture is provided
    if not request.FILES.get('profile_picture'):
      return Response({'error': 'Profile picture is required'}, 
                      status=status.HTTP_400_BAD_REQUEST)
    
    try:
      # Process file upload
      file = request.FILES['profile_picture']
      url = upload_picture(user.id, file)
      
      # Get or create user profile
      profile, created = UserProfile.objects.update_or_create(
        id=user,
        defaults={'url': url}  # This will create or update the url field
      )
        
      return Response({
        'status': 'created' if created else 'updated',
        'user_id': user.id,
        'profile_picture_url': url
      }, status=status.HTTP_200_OK)
    
    except Exception as e:
      print(f"Error saving profile: {str(e)}")
      return Response({'error': str(e)},
                      status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
  @action(detail=False, methods=['get'], url_path='profile')
  @auth_required
  def get_profile(self, request):

    ## Fetch role from query parameters
    role = request.query_params.get('role')
    if not role:
      return Response(
        {'error': 'Role is required as a query parameter'},
        status=status.HTTP_400_BAD_REQUEST
      )
    
    # Fetch user from the database
    try:
      user = User.objects.get(id=request.user_id)
    except User.DoesNotExist:
      return Response(
        {'error': 'User not found'},
        status=status.HTTP_404_NOT_FOUND
      )

    # Assign profile data from the user object
    profile_data = {
      'id': user.id,
      'email': user.email,
      'username': user.username,
      'phone': user.phone,
      'gender': user.gender
    }

    # Fetch profile picture
    try:
      profile = UserProfile.objects.get(id=request.user_id)
      profile_data['profile_picture_url'] = profile.url
    except UserProfile.DoesNotExist:
      profile_data['profile_picture_url'] = None

    try:
      if role == 'driver':
        # Fetch driver-specific data
        driver = Driver.objects.get(id=request.user_id)
        profile_data['no_of_ratings'] = driver.no_of_ratings
        profile_data['ratings'] = driver.ratings

        # Fetch vehicle information
        vehicles = Vehicle.objects.filter(user_id=request.user_id)
        profile_data['vehicles'] = [
          {
            'name': vehicle.name,
            'registration_number': vehicle.registration_number,
            'type': vehicle.type,
            'capacity': vehicle.capacity,
            'AC': vehicle.AC
          }
          for vehicle in vehicles
        ]
      elif role == 'rider':
        # Fetch rider-specific data
        rider = Rider.objects.get(id=request.user_id)
        profile_data['no_of_ratings'] = rider.no_of_ratings
        profile_data['ratings'] = rider.ratings
      else:
        return Response(
          {'error': 'Invalid role. Role must be either "driver" or "rider".'},
          status=status.HTTP_400_BAD_REQUEST
        )
    except Driver.DoesNotExist:
      return Response(
        {'error': 'Driver profile not found'},
        status=status.HTTP_404_NOT_FOUND
      )
    except Rider.DoesNotExist:
      return Response(
        {'error': 'Rider profile not found'},
        status=status.HTTP_404_NOT_FOUND
      )
    except Exception as e:
      return Response(
        {'error': 'An unexpected error occurred', 'details': str(e)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )

    return Response(profile_data, status=status.HTTP_200_OK)

  @action(detail=False, methods=['put'], url_path='profile/edit')
  @auth_required
  def edit_profile(self, request):

    try:
      user = User.objects.get(pk = request.user_id)
    except User.DoesNotExist:
      return Response(
        {'error': 'User not found'},
        status=status.HTTP_404_NOT_FOUND
      )
    ## Update user data using serializer
    try:
      serializer = self.get_serializer(
        user,
        data=request.data,
        partial=True  # Allows partial updates
      )
      serializer.is_valid(raise_exception=True)
      serializer.save()
      
      return Response(
        {
          'message': 'Profile updated successfully',
          'data': serializer.data
        },
        status=status.HTTP_200_OK
      )
      
    except ValidationError as e:
      return Response(
        {'error': 'Validation error', 'details': e.detail},
        status=status.HTTP_400_BAD_REQUEST
      )
    except Exception as e:
      return Response(
        {'error': 'An error occurred while updating the profile', 'details': str(e)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )