from rest_framework.generics import ListAPIView
from utils.permissions import SupabaseAuthenticated
from ride.serializers import RideHistorySerializer
from ride.models import RideHistory

class UserRideHistoryListApiView(ListAPIView):
    permission_classes = [SupabaseAuthenticated]  
    serializer_class = RideHistorySerializer

    def get_queryset(self):
        user_id = self.request.user_id
        user_id = 21
        return RideHistory.objects.filter(riderId=user_id)
