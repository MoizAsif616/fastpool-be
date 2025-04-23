from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from .serializers import VehicleSerializer
from user.models import User
from utils.supabase_client import supabase
from utils.decorators import auth_required

class DriverViewSet(viewsets.ModelViewSet):
  
  @action(detail=False, methods=['post'], url_path='register-vehicle')
  @auth_required
  def register_vehicle(self, request):
    try:
      # Add user_id to the request data
      vehicle_data = request.data.copy()
      vehicle_data['user_id'] = request.user_id

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