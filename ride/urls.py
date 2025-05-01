from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RideViewSet, RideSearchApiView

router = DefaultRouter()
router.register(r'', RideViewSet, basename='ride')

urlpatterns = [
  path('search/', RideSearchApiView.as_view(), name='ride-search'),
  path('', include(router.urls)),
]
