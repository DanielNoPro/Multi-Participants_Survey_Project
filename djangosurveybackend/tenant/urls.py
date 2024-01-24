from django.urls import path, include
from rest_framework_nested import routers

from tenant.views import WriteOnlyTenantView, ReadOnlyTenantView, WriteOnlyServiceView, ReadOnlyServiceView, \
    WriteOnlyUnitView, ReadOnlyUnitView, ReadOnlyConfigurationView, WriteOnlyConfigurationView

write_tenants_router = routers.SimpleRouter()
write_tenants_router.register(r'tenants', WriteOnlyTenantView, basename="Tenant write")

write_tenants_units_router = routers.NestedSimpleRouter(write_tenants_router, r'tenants', lookup='tenant')
write_tenants_units_router.register(r'tenants', WriteOnlyUnitView, basename="Unit write")

read_tenants_router = routers.SimpleRouter()
read_tenants_router.register(r'tenants', ReadOnlyTenantView, basename="Tenant read")

read_tenants_units_router = routers.NestedSimpleRouter(read_tenants_router, r'tenants', lookup='tenant')
read_tenants_units_router.register(r'tenants', ReadOnlyUnitView, basename="Unit read")

write_services_router = routers.SimpleRouter()
write_services_router.register(r'services', WriteOnlyServiceView, basename="Service write")

read_services_router = routers.SimpleRouter()
read_services_router.register(r'services', ReadOnlyServiceView, basename="Service read")

write_configs_router = routers.SimpleRouter()
write_configs_router.register(r'configs', WriteOnlyConfigurationView, basename="Config write")

read_configs_router = routers.SimpleRouter()
read_configs_router.register(r'configs', ReadOnlyConfigurationView, basename="Config read")

urlpatterns = [
    path(r'', include(read_tenants_router.urls)),
    path(r'', include(write_tenants_router.urls)),
    path(r'', include(read_tenants_units_router.urls)),
    path(r'', include(write_tenants_units_router.urls)),

    path(r'', include(read_services_router.urls)),
    path(r'', include(write_services_router.urls)),

    path(r'', include(read_configs_router.urls)),
    path(r'', include(write_configs_router.urls)),
]
