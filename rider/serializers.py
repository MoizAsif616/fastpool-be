from rest_framework import serializers
from .models import *

class RiderSerializer(serializers.ModelSerializer):
  class Meta:
    model = Rider
    fields = '__all__'

  def to_representation(self, instance):
    representation = super().to_representation(instance)
    representation.pop('id', None)  # Remove 'id' from the response
    return representation