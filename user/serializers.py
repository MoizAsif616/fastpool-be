from rest_framework import serializers
from .models import *
from utils.supabase_client import supabase
from rest_framework.exceptions import ValidationError
from driver.serializers import *
from rider.serializers import *

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
      write_only=True,  # ensures passwrd is not included in responses
      min_length=6,  
      required=False
    ) 

    class Meta:
      model = User
      # fields = ['id', 'username', 'email', 'password']
      fields = '__all__'
      read_only_fields = ['id', 'email']

    def create(self, validated_data):
      print("UserSerializer: create called")
      password = validated_data.pop('password', None)
      try:
        # Store the password in Supabase Auth
        supabase.auth.sign_up({'email':validated_data['email'], 'password':password})
      except Exception as e:
        raise ValidationError(f"Supabase Auth sign-up failed: {str(e)}")
      
      user = super().create(validated_data) 
      # Create the Driver instance using the DriverSerializer
      entity = {
        'id': user.id,  
      }

      driver_serializer = DriverSerializer(data=entity)
      if driver_serializer.is_valid():
        driver_serializer.save()
      else:
        raise serializers.ValidationError(driver_serializer.errors)
      
      rider_serializer = RiderSerializer(data=entity)
      if rider_serializer.is_valid():
        rider_serializer.save()
      else:
        raise serializers.ValidationError(rider_serializer.errors)

      return user
