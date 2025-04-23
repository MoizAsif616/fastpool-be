from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings

from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.conf import settings

class Ride(models.Model):
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='offered_rides'
    )
    source_lat = models.FloatField()  
    source_lng = models.FloatField() 
    destination_lat = models.FloatField()
    destination_lng = models.FloatField()  
    vehicle = models.ForeignKey(
        'Vehicle',  # Reference to Vehicle model
        on_delete=models.PROTECT,
        related_name='rides'
    )
    time = models.DateTimeField()
    capacity = models.PositiveIntegerField(default=1)  # Added capacity fiel
    available_seats = models.PositiveIntegerField()
    amount = models.PositiveIntegerField(default=0)  
    preferred_gender = models.CharField(
        choices=[('Male', 'Male'), ('Female', 'Female'), ('Any', 'Any')],
        default='Any'
    )
    payment_option = models.CharField(max_length=50)
    expiration_time = models.DateTimeField()
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    riders = ArrayField(
        models.IntegerField(),  # Stores user IDs instead of ForeignKey
        blank=True,
        default=list,
        help_text="Array of rider user IDs"
    )

    class Meta:
        db_table = 'rides' 

    def __str__(self):
        return f"Ride from ({self.source_lat}, {self.source_lng}) to ({self.destination_lat}, {self.destination_lng}) at {self.time}"
  
