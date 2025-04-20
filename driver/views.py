from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets,status
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from .serializers import VehicleSerializer
from user.models import User
from utils.supabase_client import supabase

class DriverViewSet(viewsets.ModelViewSet):
  

    @action(detail=False, methods=['post'], url_path='register-vehicle')
    def register_vehicle(self, request):
        # Extract token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response(
                {'error': 'Bearer token required'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        token = auth_header.split()[1]

        # Verify token with Supabase and get user email
        try:
            user_info = supabase.auth.get_user(token)
            email = user_info.user.email
        except Exception as e:
            return Response(
                {'error': 'Invalid token', 'details': str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Get user from database
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

      
        # Create vehicle
        try:
            # Add user_id to the request data
            vehicle_data = request.data.copy()
            vehicle_data['user_id'] = user.id

            serializer = VehicleSerializer(data=vehicle_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                {
                    'message': 'Vehicle registered successfully',
                    'data': serializer.data
                },
                status=status.HTTP_201_CREATED
            )
            
        except ValidationError as e:
            return Response(
                {'error': 'Validation error', 'details': e.detail},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'An error occurred while registering the vehicle', 'details': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )