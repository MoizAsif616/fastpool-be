# ride/filters.py
import django_filters
from .models import Ride

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

    class Meta:
        model = Ride
        fields = []
