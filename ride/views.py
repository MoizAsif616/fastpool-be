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
from driver.models import Vehicle  # Import Vehicle model
# Create your views here.

class RideViewSet(viewsets.ModelViewSet):
  queryset = Ride.objects.all()
  serializer_class = RideSerializer

  @action(detail=False, methods=['post'], url_path='post')
  @auth_required
  def post(self, request):
    try:
      ride_data = request.data.copy()
      ride_data['driver'] = request.user_id

      vehicle_id = ride_data.get('vehicle')
      if not vehicle_id:
        return Response(
          {'error': 'Vehicle ID is required'},
          status=status.HTTP_400_BAD_REQUEST
        )

      try:         
        vehicle = Vehicle.objects.get(pk=vehicle_id)
      except Vehicle.DoesNotExist:
        return Response(
          {'error': 'Vehicle does not exist'},
          status=status.HTTP_404_NOT_FOUND
        )

      if vehicle.driver.id != request.user_id:
        return Response(
          {'error': 'You are not authorized to use this vehicle'},
          status=status.HTTP_403_FORBIDDEN
        )

      serializer = self.get_serializer(data=ride_data)
      serializer.is_valid(raise_exception=True)
      serializer.save()

      return Response(
        {
          'message': 'Ride created successfully',
          'data': serializer.data
        },
        status=status.HTTP_201_CREATED
      )
    except Exception as e:
      return Response(
        {'error': 'An error occurred while creating the ride', 'details': str(e)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )


