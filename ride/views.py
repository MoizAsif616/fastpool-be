from django.shortcuts import render
from rest_framework import viewsets, status, generics
from .models import *
from .serializers import *
from utils.supabase_client import supabase
from rest_framework.response import Response
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from utils.helper import*
from utils.decorators import auth_required
from driver.models import Vehicle
from utils.pagination import GlobalIdCursorPagination
# Create your views here.

class RideViewSet(viewsets.ModelViewSet):
  queryset = Ride.objects.all()
  serializer_class = RideSerializer

  pagination_class = GlobalIdCursorPagination
  pagination_class.page_size = 2

  def get_queryset(self):
    queryset = super().get_queryset()

    if self.action == 'list':
      role = self.request.query_params.get('role')
      self.role = role  # Store role in the view instance for later use
      
      if role == 'driver':
        queryset = queryset.filter(driver=self.request.user_id)
      elif role == 'rider':
        queryset = queryset.exclude(driver=self.request.user_id)
            
    return queryset

  def get_serializer_context(self):
    context = super().get_serializer_context()
    context['role'] = getattr(self, 'role', None)  # Pass role to serializer context
    return context

  @auth_required
  def list(self, request, *args, **kwargs):
    try:
      if not request.query_params.get('role'):
        return Response(
          {'error': 'Role parameter is required (driver/rider)'},
          status=status.HTTP_400_BAD_REQUEST
        )
      return super().list(request, *args, **kwargs)
      
    except serializers.ValidationError as e:
      return Response(e.detail, status=e.status_code)

  @auth_required
  def create(self, request, *args, **kwargs):
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
      request.data['driver'] = request.user_id

      return super().create(request, *args, **kwargs)
    except Exception as e:
      return Response(
        {'error': 'An error occurred while creating the ride', 'details': str(e)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )

  @action(detail=False, methods=['put'], url_path='edit-ride')
  @auth_required
  def edit_ride(self, request):
    try:
      ride_id = request.query_params.get('id')  # Get ride ID from query parameters
      if not ride_id:
        return Response(
          {'error': 'Ride ID is required as a query parameter'},
          status=status.HTTP_400_BAD_REQUEST
        )

      try:
        ride = Ride.objects.get(pk=ride_id)
      except Ride.DoesNotExist:
        return Response(
          {'error': 'Ride does not exist'},
          status=status.HTTP_404_NOT_FOUND
        )

      if ride.driver.id != request.user_id:
        return Response(
          {'error': 'You are not authorized to edit this ride'},
          status=status.HTTP_403_FORBIDDEN
        )

      if ride.riders:
        return Response(
          {'error': 'Cannot edit ride as it already has riders'},
          status=status.HTTP_400_BAD_REQUEST
        )

      update_data = request.data.copy()
      vehicle_id = update_data.get('vehicle')

      if vehicle_id:
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

        update_data['vehicle'] = vehicle_id

      serializer = self.get_serializer(ride, data=update_data, partial=True)
      serializer.is_valid(raise_exception=True)
      serializer.save()

      return Response(
        {
          'message': 'Ride updated successfully',
          'data': serializer.data
        },
        status=status.HTTP_200_OK
      )
    except Exception as e:
      return Response(
        {'error': 'An error occurred while updating the ride', 'details': str(e)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )

  @auth_required
  def retrieve(self, request, *args, **kwargs):
    try:
      role = request.query_params.get('role')
      if not role:
        return Response(
          {'error': 'Role parameter is required (driver/rider)'},
          status=status.HTTP_400_BAD_REQUEST
        )

      ride_id = kwargs.get('pk')  # Get ride ID from URL parameters

      try:
        ride = Ride.objects.get(pk=ride_id)
      except Ride.DoesNotExist:
        return Response(
          {'error': 'Ride does not exist'},
          status=status.HTTP_404_NOT_FOUND
        )

      # Set the role in the serializer context
      serializer = self.get_serializer(ride, context={'role': role})
      return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
      return Response(
        {'error': 'An error occurred while retrieving the ride', 'details': str(e)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )

  @auth_required
  def destroy(self, request, *args, **kwargs):
    try:
      ride_id = kwargs.get('pk')  # Get ride ID from URL parameters
      if not ride_id:
        return Response(
          {'error': 'Ride ID is required in the URL'},
          status=status.HTTP_400_BAD_REQUEST
        )

      try:
        ride = Ride.objects.get(pk=ride_id)
      except Ride.DoesNotExist:
        return Response(
          {'error': 'Ride does not exist'},
          status=status.HTTP_404_NOT_FOUND
        )

      if ride.driver.id != request.user_id:
        return Response(
          {'error': 'You are not authorized to delete this ride'},
          status=status.HTTP_403_FORBIDDEN
        )

      if ride.riders:
        return Response(
          {'error': 'Cannot delete ride as it already has riders'},
          status=status.HTTP_400_BAD_REQUEST
        )

      ride.delete()

      return Response(
        {'message': 'Ride deleted successfully'},
        status=status.HTTP_200_OK
      )
    except Exception as e:
      return Response(
        {'error': 'An error occurred while deleting the ride', 'details': str(e)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )

# This function will be called implicitly by the server after a ride request for a certain rider is accepted.
def createRideHistory(data):
   ride_history = RideHistory.objects.create(
            riderId=data.riderId,
            source_lat=data.source_lat,
            source_lng=data.source_lng,
            destination_lat=data.destination_lat,
            destination_lng=data.destination_lng,
            date=data.date,
            time=data.time
        )
   if ride_history:
     return True
   else: return False
  


  
  
