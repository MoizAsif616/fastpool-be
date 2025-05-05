from rest_framework import serializers
from .models import *

class DriverSerializer(serializers.ModelSerializer):
  class Meta:
    model = Driver
    fields = '__all__'  # Include all fields

  def to_representation(self, instance):
    representation = super().to_representation(instance)
    representation.pop('id', None)  # Remove 'id' from the response
    return representation

class VehicleSerializer(serializers.ModelSerializer):
  class Meta:
    model = Vehicle
    fields = ['id', 'driver', 'name', 'registration_number', 'type', 'capacity', 'AC']  # Include 'id'
    extra_kwargs = {
      'driver': {'required': True},
      'name': {'required': True},
      'registration_number': {'required': True},
      'type': {'required': True},
      'capacity': {'required': True},
    }

  def to_representation(self, instance):
    representation = super().to_representation(instance)
    representation['id'] = instance.id  # Ensure 'id' is included
    return representation