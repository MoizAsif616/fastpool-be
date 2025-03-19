from rest_framework import serializers
from .models import *

class RiderSerializer(serializers.ModelSerializer):
  class Meta:
    model = Rider
    fields = '__all__'