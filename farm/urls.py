from rest_framework.routers import DefaultRouter
from farm.views.admin_views import AdminFarmViewSet, PestViewSet, BlockViewSet, SurveillancePlanViewSet, SamplingEventViewSet
from farm.views.client_views import ClientFarmViewSet

router = DefaultRouter()

# Admin routes
router.register(r'admin/farms', AdminFarmViewSet, basename='admin_farms')
router.register(r'admin/farms/(?P<farm_id>[^/.]+)/blocks', BlockViewSet, basename='admin_blocks')
router.register(r'admin/farms/(?P<farm_id>[^/.]+)/surveillance_plans', SurveillancePlanViewSet, basename='admin_surveillance_plans')
router.register(r'admin/surveillance_plans/(?P<plan_id>[^/.]+)/sampling_events', SamplingEventViewSet, basename='admin_sampling_events')
router.register(r'admin/pests', PestViewSet, basename='admin_pests')

# Client routes
router.register(r'farms', ClientFarmViewSet, basename='client_farms')

urlpatterns = router.urls
