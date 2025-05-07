import random
from datetime import datetime, timedelta, time
import django
import os
import sys
from django.utils import timezone

# Set up Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fastpool-be.settings')
django.setup()

from ride.models import Ride, RideRequest
from user.models import User
from driver.models import Vehicle
from django.db import transaction

def get_random_location():
    # Center coordinates (37.4219983, -122.084)
    # Creating a small radius around the center (approximately 1-2 km)
    lat_center = 37.4219983
    lng_center = -122.084
    
    # Adding random offset (±0.01 roughly equals 1km)
    lat_offset = random.uniform(-0.01, 0.01)
    lng_offset = random.uniform(-0.01, 0.01)
    
    return {
        'lat': round(lat_center + lat_offset, 6),
        'lng': round(lng_center + lng_offset, 6)
    }

def get_random_time():
    # Generate a random time between 6 AM and 11 PM
    start = time(6, 0)  # 6 AM
    end = time(23, 0)   # 11 PM
    
    minutes = random.randint(0, ((end.hour - start.hour) * 60))
    hour = (start.hour + minutes // 60) % 24
    minute = minutes % 60
    
    return time(hour, minute)

def get_random_future_date():
    # Generate a random date within next 30 days
    today = datetime.now().date()
    days_ahead = random.randint(0, 30)
    return today + timedelta(days=days_ahead)

def seed_rides(num_rides=10):
    try:
        # Get the driver user
        driver = User.objects.get(email="im.moiz616@gmail.com")
        rider = User.objects.get(email="shariq.munir7@gmail.com")
        
        # Get the first vehicle or create one if none exists
        # vehicle = Vehicle.objects.filter(driver=driver).first()
        vehicle_type = 'Bike'
        vehicle = Vehicle.objects.create(
            driver=driver,
            name='Toyota Corolla',
            registration_number='ABC-123',
            type=vehicle_type,
            capacity=4 if vehicle_type == 'Car' else 3,
            AC=True if vehicle_type == 'Car' else False
        )

        rides_created = []
        
        with transaction.atomic():
            for _ in range(num_rides):
                source = get_random_location()
                dest = get_random_location()
                
                # Create ride
                ride = Ride.objects.create(
                    driver=driver,
                    vehicle=vehicle,
                    source_lat=37.4219983,
                    source_lng=-122.084,
                    destination_lat=dest['lat'],
                    destination_lng=dest['lng'],
                    time=get_random_time(),
                    expiration_time=time(23, 59),  # Set to end of day
                    date=get_random_future_date(),
                    capacity=vehicle.capacity,
                    available_seats=random.randint(1, vehicle.capacity-1),
                    amount=random.randint(200, 1000),
                    preferred_gender=random.choice(['Male', 'Female', 'Any']),
                    payment_option=random.choice(['Cash', 'Online', 'Any']),
                    description=f"Ride from Location A to Location B. AC: {vehicle.AC}",
                    riders=[] if random.random() > 0.3 else [rider.id]  # 30% chance to include the rider
                )
                rides_created.append(ride)
                
        print(f"Successfully created {len(rides_created)} rides!")
        print(f"Rides with rider {rider.email}: {sum(1 for ride in rides_created if rider.id in ride.riders)}")
        
    except User.DoesNotExist as e:
        print(f"Error: {str(e)}")
        print("Please make sure both users exist in the database.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def seed_ride_requests(num_requests=5):
    try:
        # Get the rider user
        rider = User.objects.get(email="shariq.munir7@gmail.com")
        
        # Get available rides
        available_rides = Ride.objects.all()
        
        if not available_rides:
            print("No rides available to create requests for. Please run seed_rides first.")
            return
            
        requests_created = []
        
        with transaction.atomic():
            for _ in range(num_requests):
                # Get a random ride
                ride = random.choice(available_rides)
                
                # Generate random pickup location
                pickup = get_random_location()
                
                # Generate random pickup time (ensure it's before the ride time)
                ride_time_minutes = ride.time.hour * 60 + ride.time.minute
                max_minutes = max(0, ride_time_minutes - 30)  # At least 30 minutes before ride time
                pickup_minutes = random.randint(max(360, max_minutes - 60), max_minutes)  # Not earlier than 6 AM
                pickup_hour = pickup_minutes // 60
                pickup_minute = pickup_minutes % 60
                
                request = RideRequest.objects.create(
                    ride=ride,
                    rider=rider,
                    pickup_lat=pickup['lat'],
                    pickup_lng=pickup['lng'],
                    pickup_time=time(pickup_hour, pickup_minute),
                    status='pending'
                )
                requests_created.append(request)
                
        print(f"Successfully created {len(requests_created)} ride requests!")
        
    except User.DoesNotExist as e:
        print(f"Error: {str(e)}")
        print("Please make sure the rider exists in the database.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # print("Starting ride seeding process...")
    # seed_rides()
    print("Starting ride request seeding process...")
    seed_ride_requests()
    print("Seeding completed!") 