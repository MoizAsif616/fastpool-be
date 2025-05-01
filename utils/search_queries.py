# Possible Search Queries for Ride Filtering

# 1. **Date Range Filters**
#    - Filter rides where the ride date is after a certain date.
#    - Example query: `/rides/search/?date_after=2025-05-01`
#    - Filter rides where the ride date is before a certain date.
#    - Example query: `/rides/search/?date_before=2025-05-01`

# 2. **Time Window (Datetime) Filters**
#    - Filter rides where the ride time is after a certain datetime.
#    - Example query: `/rides/search/?time_after=2025-05-01T14:00:00`
#    - Filter rides where the ride time is before a certain datetime.
#    - Example query: `/rides/search/?time_before=2025-05-01T16:00:00`

# 3. **Choice Filters**
#    - Filter rides by preferred gender.
#    - Example query: `/rides/search/?preferred_gender=Male`
#    - Filter rides by payment option (e.g., cash, card, etc.).
#    - Example query: `/rides/search/?payment_option=Card`

# 4. **Numeric Range Filters**
#    - Filter rides where the amount is greater than or equal to a specific value.
#    - Example query: `/rides/search/?min_amount=10.0`
#    - Filter rides where the amount is less than or equal to a specific value.
#    - Example query: `/rides/search/?max_amount=50.0`
#    - Filter rides where the available seats are greater than or equal to a certain value.
#    - Example query: `/rides/search/?min_seats=2`

# 5. **Text Search in Ride Description**
#    - Filter rides based on a partial match in the description field.
#    - Example query: `/rides/search/?description=night%20ride`

# 6. **Vehicle Type Search**
#    - Filter rides based on the type of vehicle associated with the ride (e.g., sedan, SUV).
#    - Example query: `/rides/search/?vehicle_type=sedan`

# **Combined Queries (Multiple Filters)**
#    - You can combine multiple filters to refine the search.
#    - Example query (Date after + Vehicle Type):
#      `/rides/search/?date_after=2025-05-01&vehicle_type=sedan`
#    - Example query (Amount range + Seats available):
#      `/rides/search/?min_amount=10.0&max_amount=50.0&min_seats=2`
