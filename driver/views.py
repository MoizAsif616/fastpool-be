from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from ride.models import Ride
from ride.serializers import RideSerializer
from .serializers import VehicleSerializer
from user.models import User
from utils.supabase_client import supabase
from utils.decorators import auth_required
from utils import *
from django.utils import timezone
from datetime import timedelta

class DriverViewSet(viewsets.ModelViewSet):
  
  @action(detail=False, methods=['post'], url_path='vehicles/register')
  @auth_required
  def register_vehicle(self, request):
    try:
      # Add user_id to the request data
      vehicle_data = request.data.copy()
      vehicle_data['driver'] = request.user_id

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

  @action(detail=False, methods=['get'], url_path='vehicles/get')
  @auth_required
  def get_vehicles(self, request):
    try:
      # Fetch all vehicles associated with the authenticated driver
      vehicles = Vehicle.objects.filter(driver=request.user_id)
      vehicle_data = VehicleSerializer(vehicles, many=True).data

      return Response(
        {
          'message': 'Vehicles retrieved successfully',
          'data': vehicle_data
        },
        status=status.HTTP_200_OK
      )
    except ObjectDoesNotExist:
      return Response(
        {'error': 'No vehicles found for the driver'},
        status=status.HTTP_404_NOT_FOUND
      )
    except Exception as e:
      return Response(
        {'error': 'An error occurred while fetching vehicles', 'details': str(e)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )

  @action(detail=False, methods=['delete'], url_path='vehicles/delete')
  @auth_required
  def delete_vehicle(self, request):
    try:
      vehicle_id = request.data.get('id')
      if not vehicle_id:
        return Response(
          {'error': 'Vehicle ID is required'},
          status=status.HTTP_400_BAD_REQUEST
        )

      # Check if the vehicle exists and belongs to the authenticated driver
      vehicle = Vehicle.objects.filter(id=vehicle_id, driver=request.user_id).first()
      if not vehicle:
        return Response(
          {'error': 'Vehicle not found or does not belong to the driver'},
          status=status.HTTP_404_NOT_FOUND
        )

      # Check if the vehicle is in use in the Ride table
      if Ride.objects.filter(vehicle=vehicle).exists():
        return Response(
          {'error': 'Vehicle cannot be deleted as it is in use in rides'},
          status=status.HTTP_400_BAD_REQUEST
        )

      # Delete the vehicle
      vehicle.delete()
      return Response(
        {'message': 'Vehicle deleted successfully'},
        status=status.HTTP_200_OK
      )

    except Exception as e:
      return Response(
        {'error': 'An error occurred while deleting the vehicle', 'details': str(e)},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
      )

  @action(detail=False, methods=['get'])
  @auth_required
  def homepage(self, request):   
    
    response_data = {}
    # print(f"Request data: {request.data}")
    
    try:
        # Get  driver profile
        driver = Driver.objects.get(id=request.user_id)
        print(f"Driver: {driver}")
        recent_rides = Ride.objects.filter(
            driver=request.user_id,  # Using the user object
        )
        response_data['active_rides'] = recent_rides.count()
      
        # Upcoming rides (filtered by current driver)
        
        upcoming_ride = Ride.objects.filter(
            driver=request.user_id,
            ride_time__gte=timezone.now()  # Only future rides
        ).order_by('time').first()

        response_data['upcoming_ride'] = RideSerializer(upcoming_ride).data if upcoming_ride else None
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found in database'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"Error in homepage view: {str(e)}")
        return Response(
            {'error': 'Internal server error', 'details': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )