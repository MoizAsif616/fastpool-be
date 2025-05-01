from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'rides', RideViewSet, basename='ride')
router.register(r'ride/requests', RideRequestViewSet, basename='ride-request') 

urlpatterns = [
  path('search/', RideSearchApiView.as_view(), name='ride-search'),
  path('', include(router.urls)),
]
