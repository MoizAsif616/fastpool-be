from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

urlpatterns = [
  path('history/', UserRideHistoryListApiView.as_view()),
  path('homepage/', HomepageView.as_view())
]

