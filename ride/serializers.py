from rest_framework import serializers
from .models import *
from user.serializers import UserSerializer  # Import UserSerializer
from driver.serializers import VehicleSerializer  # Import VehicleSerializer
from user.models import User 

class RideSerializer(serializers.ModelSerializer):
  class Meta:
    model = Ride
    fields = '__all__'

  def to_representation(self, instance):
    representation = super().to_representation(instance)
    role = self.context.get('role')  # Get role from serializer context

    if role == 'rider':
      representation['driver'] = UserSerializer(instance.driver).data
    elif role == 'driver':
      representation.pop('driver', None)  # Remove driver data from response

    representation['vehicle'] = VehicleSerializer(instance.vehicle).data

    # Fetch rider information using UserSerializer
    rider_ids = representation.get('riders', [])
    riders_info = []
 
    for rider_id in rider_ids:
      try:
        user = User.objects.get(id=rider_id)
        riders_info.append(UserSerializer(user).data)
      except User.DoesNotExist:
        continue
    representation['riders'] = riders_info

    return representation


class RideRequestSerializer(serializers.ModelSerializer):
  class Meta:
    model = RideRequest
    fields = '__all__'

  def to_representation(self, instance):
    representation = super().to_representation(instance)
    role = self.context.get('role')  # Get role from serializer context

    if role == 'driver':
      # Replace rider ID with full rider information
      representation['rider'] = UserSerializer(instance.rider).data

    return representation