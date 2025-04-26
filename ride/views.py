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
      ride_data['driver'] = request.user_id  # Ensure driver_id is set

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

class RideRequestViewSet(viewsets.ModelViewSet):
  queryset = RideRequest.objects.all()
  serializer_class = RideRequestSerializer
  http_method_names = ['get', 'post', 'delete'] 

  def get_queryset(self):
    queryset = super().get_queryset()
    role = self.request.query_params.get('role')

    if not role:
      return queryset.none()  # Return empty if no role is provided

    if role == 'rider':
      queryset = queryset.filter(rider=self.request.user_id)
    elif role == 'driver':
      ride_id = self.request.query_params.get('id')
      if not ride_id:
          return queryset.none()  # Return empty if no ride_id for driver
      queryset = queryset.filter(ride_id=ride_id, ride__driver=self.request.user_id)
    
    return queryset

  def get_serializer_context(self):
    context = super().get_serializer_context()
    context['role'] = self.request.query_params.get('role')  # Pass role to serializer
    return context

  @auth_required
  def list(self, request, *args, **kwargs):
    role = request.query_params.get('role')
    if not role:
      return Response(
        {'error': 'Role parameter is required (driver/rider)'},
        status=status.HTTP_400_BAD_REQUEST
      )

    if role != 'rider' and role != 'driver':
      return Response(
        {'error': 'Invalid role parameter. Use "driver" or "rider".'},
        status=status.HTTP_400_BAD_REQUEST
      )
    
    if role == 'driver':
      ride_id = request.query_params.get('id')
      if not ride_id:
        return Response(
          {'error': 'Ride ID is required as query parameter for driver role'},
          status=status.HTTP_400_BAD_REQUEST
        )

      try:
        Ride.objects.get(pk=ride_id, driver=request.user_id)
      except Ride.DoesNotExist:
        return Response(
          {'error': 'Ride does not exist or you are not the driver'},
          status=status.HTTP_404_NOT_FOUND
        )
    
    # Let get_queryset() handle filtering
    return super().list(request, *args, **kwargs)

  @auth_required
  def create(self, request, *args, **kwargs):
    try:
      ride_id = request.data.get('ride')
      if not ride_id:
        return Response(
          {'error': 'Ride ID is required'},
          status=status.HTTP_400_BAD_REQUEST
        )

      try:
        ride = Ride.objects.get(pk=ride_id)
      except Ride.DoesNotExist:
        return Response(
          {'error': 'Ride does not exist'},
          status=status.HTTP_404_NOT_FOUND
        )

      # Check if the ride has available seats
      if ride.available_seats == 0:
        return Response(
          {'error': 'Ride has no available seats'},
          status=status.HTTP_400_BAD_REQUEST
        )

      # Check if the driver of the ride is the same as the request user
      if ride.driver.id == request.user_id:
        return Response(
          {'error': 'You cannot create a ride request for your own ride'},
          status=status.HTTP_400_BAD_REQUEST
        )

      request.data['rider'] = request.user_id
      request.data['status'] = 'pending'

      super().create(request, *args, **kwargs)

      return Response({"message": "Ride request created successfully."}, status=status.HTTP_201_CREATED)

    except Exception as e:
      return Response(
        {'error': 'An error occurred while creating the ride request', 'details': str(e)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )

  @auth_required
  def destroy(self, request, *args, **kwargs):
    try:
      ride_request_id = kwargs.get('pk')  
      if not ride_request_id:
        return Response(
          {'error': 'Ride request ID is required in the URL'},
          status=status.HTTP_400_BAD_REQUEST
        )
      try:
        ride_request = RideRequest.objects.get(pk=ride_request_id)
      except RideRequest.DoesNotExist:
        return Response(
          {'error': 'Ride request does not exist'},
          status=status.HTTP_404_NOT_FOUND
        )

      if ride_request.rider.id != request.user_id:
        return Response(
          {'error': 'You are not authorized to delete this ride request'},
          status=status.HTTP_403_FORBIDDEN
        )
      
      if ride_request.status == 'accepted':
        return Response(
          {'error': 'Accepted ride requests cannot be deleted'},
          status=status.HTTP_400_BAD_REQUEST
        )

      ride_request.delete()

      return Response(
        {'message': 'Ride request deleted successfully'},
        status=status.HTTP_200_OK
      )
    except Exception as e:
      return Response(
        {'error': 'An error occurred while deleting the ride request', 'details': str(e)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )

  @action(detail=False, methods=['post'], url_path='deny')
  @auth_required
  def deny(self, request):
    try:
      ride_request_id = request.data.get('id')  # Get the request ID from the body
      if not ride_request_id:
        return Response(
          {'error': 'Ride request ID is required in the body'},
          status=status.HTTP_400_BAD_REQUEST
        )

      try:
        ride_request = RideRequest.objects.get(pk=ride_request_id)
      except RideRequest.DoesNotExist:
        return Response(
          {'error': 'Ride request does not exist'},
          status=status.HTTP_404_NOT_FOUND
        )

      if ride_request.ride.driver.id != request.user_id:
        return Response(
          {'error': 'You are not authorized to deny this ride request'},
          status=status.HTTP_403_FORBIDDEN
        )

      if ride_request.status != 'pending':
        return Response(
          {'error': 'Only pending requests can be denied'},
          status=status.HTTP_400_BAD_REQUEST
        )

      # Update the status to denied
      ride_request.status = 'denied'
      ride_request.save()

      return Response(
        {'message': 'Ride request has been denied successfully'},
        status=status.HTTP_200_OK
      )
    except Exception as e:
      return Response(
        {'error': 'An error occurred while denying the ride request', 'details': str(e)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )

  @action(detail=False, methods=['post'], url_path='accept')
  @auth_required
  def accept(self, request):
    try:
      ride_request_id = request.data.get('id')  # Get the request ID from the body
      if not ride_request_id:
        return Response(
          {'error': 'Ride request ID is required in the body'},
          status=status.HTTP_400_BAD_REQUEST
        )

      try:
        ride_request = RideRequest.objects.get(pk=ride_request_id)
      except RideRequest.DoesNotExist:
        return Response(
          {'error': 'Ride request does not exist'},
          status=status.HTTP_404_NOT_FOUND
        )

      if ride_request.ride.driver.id != request.user_id:
        return Response(
          {'error': 'You are not authorized to accept this ride request'},
          status=status.HTTP_403_FORBIDDEN
        )

      if ride_request.status == 'denied':
        return Response(
          {'error': 'This ride request has already been denied'},
          status=status.HTTP_400_BAD_REQUEST
        )

      ride = ride_request.ride
      if ride.available_seats <= 0:
        return Response(
          {'error': 'No available seats in the ride'},
          status=status.HTTP_400_BAD_REQUEST
        )

      ride_request.status = 'accepted'
      ride_request.save()

      ride.available_seats -= 1
      ride.riders.append(ride_request.rider.id)  
      ride.save()

      if ride.available_seats == 0:
        RideRequest.objects.filter(ride=ride, status='pending').update(status='capacity-full')

      return Response(
        {'message': 'Ride request has been accepted successfully'},
        status=status.HTTP_200_OK
      )
    except Exception as e:
      return Response(
        {'error': 'An error occurred while accepting the ride request', 'details': str(e)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )