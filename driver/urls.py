
from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter
from .serializers import *

router = DefaultRouter()
router.register(r'', DriverViewSet, basename='driver')

urlpatterns = [
  path('', include(router.urls)),
  

]