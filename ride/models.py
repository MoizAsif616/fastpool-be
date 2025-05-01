from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings
from user.models import User
from driver.models import Vehicle


class Ride(models.Model):
    driver = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="offered_rides"
    )
    source_lat = models.FloatField()
    source_lng = models.FloatField()
    destination_lat = models.FloatField()

    destination_lng = models.FloatField()
    vehicle = models.ForeignKey(Vehicle, on_delete=models.PROTECT, related_name="rides")
    time = models.TimeField()
    capacity = models.PositiveIntegerField(default=1)

    available_seats = models.PositiveIntegerField()
    amount = models.PositiveIntegerField(default=0)
    preferred_gender = models.CharField(
        choices=[("Male", "Male"), ("Female", "Female"), ("Any", "Any")], default="Any"
    )
    payment_option = models.CharField(
        choices=[("Cash", "Cash"), ("Online", "Online"), ("Any", "Any")], default="Any"
    )
    expiration_time = models.TimeField()
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    riders = ArrayField(
        models.IntegerField(),  # Stores user IDs instead of ForeignKey
        blank=True,
        default=list,
        help_text="Array of rider user IDs",
    )

    class Meta:
        ordering = ["-id"]
        db_table = "ride"

    def __str__(self):
        return f"Ride from ({self.source_lat}, {self.source_lng}) to ({self.destination_lat}, {self.destination_lng}) at {self.time}"

class RideRequest(models.Model):
  ride = models.ForeignKey('ride.Ride', on_delete=models.CASCADE, related_name='requests')
  rider = models.ForeignKey('user.User', on_delete=models.CASCADE, related_name='requests')
  pickup_lat = models.FloatField()
  pickup_lng = models.FloatField()
  pickup_time = models.TimeField()
  status = models.CharField(choices=[
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
    ('completed', 'Completed')
  ], default='pending')

  class Meta:
    db_table = 'ride_request'
    ordering = ['id']

class RideHistory(models.Model):
    riderId = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="ride_history"
    )
    source_lat = models.FloatField()
    source_lng = models.FloatField()
    destination_lat = models.FloatField()
    destination_lng = models.FloatField()
    date = models.DateField()
    time = models.TimeField()

