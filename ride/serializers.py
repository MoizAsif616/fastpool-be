from rest_framework import serializers
from .models import Ride
from user.serializers import UserSerializer  # Import UserSerializer
from driver.serializers import VehicleSerializer  # Import VehicleSerializer

class RideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = '__all__'  # Include all fields

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('id', None)
        # Replace driver and vehicle IDs with their full objects
        representation['driver'] = UserSerializer(instance.driver).data
        representation['vehicle'] = VehicleSerializer(instance.vehicle).data
        
        return representation

    def update(self, instance, validated_data):
        # Prevent updating driver and vehicle
        validated_data.pop('driver', None)
        validated_data.pop('vehicle', None)
        return super().update(instance, validated_data)
