from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from utils.permissions import SupabaseAuthenticated
from rest_framework.response import Response
from ride.serializers import RideHistorySerializer 
from ride.models import RideHistory, RideRequest, Ride
import random
from django.utils import timezone

class UserRideHistoryListApiView(ListAPIView):
    permission_classes = [SupabaseAuthenticated]  
    serializer_class = RideHistorySerializer

    def get_queryset(self):
        user_id = self.request.user_id
        return RideHistory.objects.filter(riderId=user_id)
    
    
class HomepageView(APIView):
    permission_classes = [SupabaseAuthenticated]
    
    def get(self, request):
        user = request.user

        # Pending Requests Count
        pending_requests = RideRequest.objects.filter(rider=user, status='pending')

        pending_count = pending_requests.count()
        
        # Rider Rating. For now it is a random number btw [3.0, 5.0].
        rating = round(random.uniform(3.0, 5.0), 1)
        
        # Get today's date and current time
        today = timezone.now().date()
        now = timezone.now().time()

        # Filter upcoming rides where the user ID is in the riders array
        upcoming_ride = (
            Ride.objects
            .filter(riders__contains=[user.id], date__gte=today)
            .order_by('date', 'time')  # earliest upcoming ride
            .first()
        )

        # Prepare ride data if any found
        ride_data = None
        if upcoming_ride:
            ride_data = {
                'ride_id': upcoming_ride.id,
                'source_lat': upcoming_ride.source_lat,
                'source_lng': upcoming_ride.source_lng,
                'destination_lat': upcoming_ride.destination_lat,
                'destination_lng': upcoming_ride.destination_lng,
                'date': upcoming_ride.date,
                'time': upcoming_ride.time,
                'driver_id': upcoming_ride.driver.id,
                'vehicle_id': upcoming_ride.vehicle.id,
                'available_seats': upcoming_ride.available_seats,
                'amount': upcoming_ride.amount,
                'preferred_gender': upcoming_ride.preferred_gender,
                'payment_option': upcoming_ride.payment_option,
                'vehicle_type': upcoming_ride.vehicle.type,
                'vehicle_reg#': upcoming_ride.vehicle.registration_number,
                'ac':upcoming_ride.vehicle.AC
            }
        
        
        results = {
            "pending_requests_count": pending_count,
            'upcoming_ride': ride_data,
            "rating": rating
        }
        
        
        
        return Response({'Results': results})






