from django.db import models
from user.models import User
# Create your models here.


class Rider(models.Model):
  id = models.OneToOneField(
    User, 
    on_delete=models.CASCADE, 
    primary_key=True  # Use the User's Supabase ID as the primary key
  )
  no_of_ratings = models.IntegerField(default=0)
  ratings = models.FloatField(default=0.0)

  class Meta:
    db_table = 'rider'