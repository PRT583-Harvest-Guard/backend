from django.urls import path,include
from rest_framework.routers import DefaultRouter
from farm import views

router = DefaultRouter()
router.register(r'farms', views.FarmViewSet, basename='farm')
router.register(r'boundary-points', views.BoundaryPointViewSet, basename='boundary-point')
router.register(r'observation-points', views.ObservationPointViewSet, basename='observation-point')
router.register(r'inspection-suggestions', views.InspectionSuggestionViewSet, basename='inspection-suggestion')
router.register(r'inspection-observations', views.InspectionObservationViewSet, basename='inspection-observation')

urlpatterns = [
    path('', include(router.urls)),
    path('sync-data/', views.SyncDataAPIView.as_view(), name='sync-data')
]
