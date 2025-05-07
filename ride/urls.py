from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'requests', RideRequestViewSet, basename='ride-request')  # Removed 'ride/' prefix
router.register(r'', RideViewSet, basename='ride')  # Changed from 'rides' to '' since we're at root

urlpatterns = [
    path('search/', RideSearchApiView.as_view(), name='ride-search'),
    path('', include(router.urls)),
]
