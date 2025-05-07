from django.db.models import Q, F, ExpressionWrapper, FloatField, Value
import django_filters
from .models import Ride
from django.db.models.functions import Power, Sqrt

class RideFilter(django_filters.FilterSet):
    # Date range
    date_after = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_before = django_filters.DateFilter(field_name="date", lookup_expr="lte")

    # Time window (datetime)
    time_after = django_filters.DateTimeFilter(field_name="time", lookup_expr="gte")
    time_before = django_filters.DateTimeFilter(field_name="time", lookup_expr="lte")

    # Choice filters
    preferred_gender = django_filters.ChoiceFilter(
        choices=Ride._meta.get_field("preferred_gender").choices
    )
    payment_option = django_filters.ChoiceFilter(
        choices=Ride._meta.get_field("payment_option").choices
    )

    # Numeric ranges
    min_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="gte")
    max_amount = django_filters.NumberFilter(field_name="amount", lookup_expr="lte")
    min_seats = django_filters.NumberFilter(
        field_name="available_seats", lookup_expr="gte"
    )

    # Text search in description
    description = django_filters.CharFilter(
        field_name="description", lookup_expr="icontains"
    )

    # Search by vehicle type
    vehicle_type = django_filters.CharFilter(
        field_name="vehicle__type", lookup_expr="icontains", label="Vehicle Type"
    )

    # Geolocation filters
    source_lat = django_filters.NumberFilter(method='filter_by_source_location')
    source_lng = django_filters.NumberFilter()
    destination_lat = django_filters.NumberFilter(method='filter_by_destination_location')
    destination_lng = django_filters.NumberFilter()

    def filter_by_source_location(self, queryset, name, value):
        if value and self.data.get('source_lng'):
            lat = float(value)
            lng = float(self.data['source_lng'])
            
            # Create a bounding box of roughly 5km
            lat_range = 0.045  # Approximately 5km in latitude
            lng_range = 0.045  # Approximately 5km in longitude
            
            # First filter by bounding box to reduce the number of distance calculations
            filtered_queryset = queryset.filter(
                source_lat__range=(lat - lat_range, lat + lat_range),
                source_lng__range=(lng - lng_range, lng + lng_range)
            )

            # Calculate approximate distance using Euclidean distance
            # This is not as accurate as Haversine but works well enough for small distances
            # and can be calculated entirely in the database
            lat_diff = ExpressionWrapper(
                Power(F('source_lat') - Value(lat), 2) * 111.32 * 111.32,
                output_field=FloatField()
            )
            lng_diff = ExpressionWrapper(
                Power(F('source_lng') - Value(lng), 2) * 111.32 * 111.32,
                output_field=FloatField()
            )
            
            distance = ExpressionWrapper(
                Sqrt(lat_diff + lng_diff),
                output_field=FloatField()
            )
            
            filtered_queryset = filtered_queryset.annotate(
                distance=distance
            ).filter(distance__lte=5)
            
            return filtered_queryset
            
        return queryset

    def filter_by_destination_location(self, queryset, name, value):
        if value and self.data.get('destination_lng'):
            lat = float(value)
            lng = float(self.data['destination_lng'])
            
            # Create a bounding box of roughly 5km
            lat_range = 0.045  # Approximately 5km in latitude
            lng_range = 0.045  # Approximately 5km in longitude
            
            # First filter by bounding box to reduce the number of distance calculations
            filtered_queryset = queryset.filter(
                destination_lat__range=(lat - lat_range, lat + lat_range),
                destination_lng__range=(lng - lng_range, lng + lng_range)
            )

            # Calculate approximate distance using Euclidean distance
            lat_diff = ExpressionWrapper(
                Power(F('destination_lat') - Value(lat), 2) * 111.32 * 111.32,
                output_field=FloatField()
            )
            lng_diff = ExpressionWrapper(
                Power(F('destination_lng') - Value(lng), 2) * 111.32 * 111.32,
                output_field=FloatField()
            )
            
            distance = ExpressionWrapper(
                Sqrt(lat_diff + lng_diff),
                output_field=FloatField()
            )
            
            filtered_queryset = filtered_queryset.annotate(
                distance=distance
            ).filter(distance__lte=5)
            
            return filtered_queryset
            
        return queryset

    class Meta:
        model = Ride
        fields = []
