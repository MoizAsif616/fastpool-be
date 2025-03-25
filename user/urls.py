from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter
from .serializers import *

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
  path('', include(router.urls)),
  

]