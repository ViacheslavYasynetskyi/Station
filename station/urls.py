from django.urls import path, include

from rest_framework import routers

from station.views import (
    # BusList,
    # BusDetail,
    BusViewSet, TripViewSet, FacilityViewSet, OrderViewSet
)

# bus_list = BusViewSet.as_view(actions={
#     "get": "list",
#     "post": "create",
# })
# bus_detail = BusViewSet.as_view(actions={
#     "get": "retrieve",
#     "put": "update",
#     "patch": "partial_update",
#     "delete": "destroy",
# })
#
# urlpatterns = [
#     path("buses/", bus_list, name="bus-list"),
#     path("buses/<int:pk>/", bus_detail, name="bus-detail"),
# ]

router = routers.DefaultRouter()
router.register("facilities", FacilityViewSet)
router.register("buses", BusViewSet)
router.register("trips", TripViewSet)
router.register("orders", OrderViewSet)

urlpatterns = [
    path("", include(router.urls))
]

app_name = "station"
