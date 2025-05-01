# permissions.py
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed, NotFound
from user.models import User
from utils.supabase_client import supabase
from rest_framework import status

class SupabaseAuthenticated(BasePermission):
    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise AuthenticationFailed(
                {'error': 'Authorization header missing or invalid'},
                code=status.HTTP_401_UNAUTHORIZED
            )

        token = auth_header.split()[1]

        try:
            supabase_user = supabase.auth.get_user(token).user

            try:
                user = User.objects.get(email=supabase_user.email)
                request.user_id = user.id  # You can set it here too
                request.user = user        # Even better, set `request.user`
            except User.DoesNotExist:
                raise NotFound(
                    {'error': 'User not found in database'},
                    code=status.HTTP_404_NOT_FOUND
                )

            return True

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
