from django.db import models
from user.models import User
# Create your models here.


class Driver(models.Model):
  id = models.OneToOneField(
    User, 
    on_delete=models.CASCADE, 
    primary_key=True,  # Use the User's Supabase ID as the primary key
    db_column='id'
  )
  no_of_ratings = models.IntegerField(default=0)
  ratings = models.FloatField(default=0.0)

  class Meta:
    db_table = 'driver'



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
      return self.registration_number

