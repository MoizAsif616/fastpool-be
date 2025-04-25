from functools import wraps
from rest_framework.exceptions import AuthenticationFailed, NotFound
from user.models import User
from utils.supabase_client import supabase
from rest_framework import status

def auth_required(view_func):
  @wraps(view_func)
  def wrapped_view(self, request, *args, **kwargs):
    # Check Authorization Header
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
      raise AuthenticationFailed(
        {'error': 'Authorization header missing or invalid'},
        code=status.HTTP_401_UNAUTHORIZED
      )
    
    token = auth_header.split()[1]
    
    try:
      # Verify Supabase Token
      supabase_user = supabase.auth.get_user(token).user
      
      # Get User from db
      try:
        user = User.objects.get(email=supabase_user.email)
        request.user_id = user.id
      except User.DoesNotExist:
        raise NotFound(
          {'error': 'User not found in database'},
          code=status.HTTP_404_NOT_FOUND
        )
      
      return view_func(self, request, *args, **kwargs)
      
    except Exception as e:
      if "Invalid token" in str(e):
        raise AuthenticationFailed(
          {'error': 'Invalid or expired token'},
          code=status.HTTP_401_UNAUTHORIZED
        )
      raise AuthenticationFailed(
        {'error': 'Authentication failed', 'details': str(e)},
        code=status.HTTP_401_UNAUTHORIZED
      )
  
  return wrapped_view