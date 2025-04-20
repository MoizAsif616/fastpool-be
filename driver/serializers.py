from rest_framework import serializers
from .models import *

class DriverSerializer(serializers.ModelSerializer):
  class Meta:
    model = Driver
    fields = '__all__'

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ['user_id','name', 'registration_number', 'type', 'capacity', 'AC']
        extra_kwargs = {
            'user_id': {'required': True},
            'name': {'required': True},
            'registration_number': {'required': True},
            'type': {'required': True},
            'capacity': {'required': True},
            
        }    