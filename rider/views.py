from rest_framework.generics import ListAPIView
from utils.permissions import SupabaseAuthenticated
from ride.serializers import RideHistorySerializer, RideSerializer
from ride.models import RideHistory, Ride


class UserRideHistoryListApiView(ListAPIView):
    permission_classes = [SupabaseAuthenticated]  
    serializer_class = RideHistorySerializer

    def get_queryset(self):
        user_id = self.request.user_id
        return RideHistory.objects.filter(riderId=user_id)

