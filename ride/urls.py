from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RideViewSet, RideHistoryListApiView

router = DefaultRouter()
router.register(r'', RideViewSet, basename='ride')

urlpatterns = [
  path('history/', RideHistoryListApiView.as_view()),
  path('', include(router.urls)),
]
