from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserRideHistoryListApiView

urlpatterns = [
  path('history/', UserRideHistoryListApiView.as_view()),
]

