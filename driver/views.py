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
  
  @action(detail=False, methods=['post'], url_path='register-vehicle')
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

  @action(detail=False, methods=['get'])
  @auth_required
  def homepage(self, request):   
    role = request.query_params.get('role')
    if not role:
        return Response(
            {'error': 'Role parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    response_data = {}
    now = timezone.now()
    
    try:
        # Get the user object
        user = User.objects.get(id=request.user_id)
        # Get  driver profile
        driver = Driver.objects.get(id=request.user_id)
        # Rides in last 30 days (filtered by current driver)
        thirty_days_ago = now - timedelta(days=30)
        recent_rides = Ride.objects.filter(
            driver=user,  # Using the user object
            date__gte=thirty_days_ago.date()
        )
        response_data['rides_last_30_days'] = recent_rides.count()
        
        # Ratings (only for drivers)
        if role == 'driver':
            avg_rating = driver.ratings / driver.no_of_ratings if driver.no_of_ratings > 0 else 0
            response_data['ratings'] = {
                'average_rating': round(avg_rating, 2),
                'total_ratings': driver.no_of_ratings
            }
        
        # Upcoming rides (filtered by current driver)
        twelve_hours_later = now + timedelta(hours=12)
        upcoming_rides = Ride.objects.filter(
            driver=user,  # Using the user object
            time__gte=now,
            time__lte=twelve_hours_later
        ).order_by('time')
        
        response_data['upcoming_rides'] = RideSerializer(upcoming_rides, many=True).data
        
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
