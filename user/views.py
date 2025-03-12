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
# Create your views here.

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
      if user.is_verified:
        return Response({'error': 'User is not verified.'}, status=status.HTTP_403_FORBIDDEN)
        
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
  


