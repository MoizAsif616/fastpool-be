from django.db import models
from user.models import *

# Create your models here.
class Vehicle(models.Model):
  user_id = models.ForeignKey(User, on_delete=models.CASCADE)
  name = models.CharField(max_length=255)
  registration_number = models.CharField(max_length=255)
  type = models.CharField(max_length=255)
  capacity = models.IntegerField(default=0)
  AC = models.BooleanField(default=False)
  
  class Meta:
    db_table = 'vehicle'
    
  def __str__(self):
    return self.vehicle_number