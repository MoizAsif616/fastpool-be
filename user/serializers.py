from rest_framework import serializers
from .models import *
from utils.supabase_client import supabase
from rest_framework.exceptions import ValidationError

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
      write_only=True,  # ensures passwrd is not included in responses
      min_length=6,  
    ) 

    class Meta:
      model = User
      # fields = ['id', 'username', 'email', 'password']
      fields = '__all__'

    def create(self, validated_data):
      print("UserSerializer: create called")
      password = validated_data.pop('password', None)
      try:
        # Store the password in Supabase Auth
        supabase.auth.sign_up({'email':validated_data['email'], 'password':password})
      except Exception as e:
        raise ValidationError(f"Supabase Auth sign-up failed: {str(e)}")
      
      user = super().create(validated_data) 
      return user

    def update(self, instance, validated_data):
        print("UserSerializer: update called")
        return super().update(instance, validated_data)