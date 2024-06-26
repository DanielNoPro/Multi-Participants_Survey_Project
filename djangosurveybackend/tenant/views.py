from abc import ABC

from rest_framework.authentication import BasicAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from verification.authentication import ExpiringTokenAuthentication

from core.views.viewsets import ReadOnlyModelViewSet, WriteOnlyViewSet
from tenant.models import Configuration, Service, Tenant, Unit
from tenant.serializers import (
    ConfigurationSerializer,
    ServiceSerializer,
    TenantSerializer,
    UnitSerializer,
)


# Create your views here.
class CoreTenantView(ABC):
    lookup_field = "id"
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer


@permission_classes([IsAuthenticated, IsAdminUser])
@authentication_classes([JWTAuthentication, BasicAuthentication])
class WriteOnlyTenantView(CoreTenantView, WriteOnlyViewSet):
    pass


@permission_classes([IsAuthenticated])
@authentication_classes(
    [JWTAuthentication, ExpiringTokenAuthentication, BasicAuthentication]
)
class ReadOnlyTenantView(CoreTenantView, ReadOnlyModelViewSet):
    pass


class CoreServiceView(ABC):
    lookup_field = "id"
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


@permission_classes([IsAuthenticated, IsAdminUser])
@authentication_classes([JWTAuthentication, BasicAuthentication])
class WriteOnlyServiceView(CoreServiceView, WriteOnlyViewSet):
    pass


@permission_classes([IsAuthenticated])
@authentication_classes(
    [JWTAuthentication, ExpiringTokenAuthentication, BasicAuthentication]
)
class ReadOnlyServiceView(CoreServiceView, ReadOnlyModelViewSet):
    pass


class CoreUnitView(ABC):
    lookup_field = "id"
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer


@permission_classes([IsAuthenticated, IsAdminUser])
@authentication_classes([JWTAuthentication, BasicAuthentication])
class WriteOnlyUnitView(CoreUnitView, WriteOnlyViewSet):
    pass


@permission_classes([IsAuthenticated])
@authentication_classes(
    [JWTAuthentication, ExpiringTokenAuthentication, BasicAuthentication]
)
class ReadOnlyUnitView(CoreUnitView, ReadOnlyModelViewSet):
    pass


class CoreConfigurationView(ABC):
    lookup_field = "id"
    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer


@permission_classes([IsAuthenticated, IsAdminUser])
@authentication_classes([JWTAuthentication, BasicAuthentication])
class WriteOnlyConfigurationView(CoreConfigurationView, WriteOnlyViewSet):
    pass


@permission_classes([IsAuthenticated])
@authentication_classes(
    [JWTAuthentication, ExpiringTokenAuthentication, BasicAuthentication]
)
class ReadOnlyConfigurationView(CoreConfigurationView, ReadOnlyModelViewSet):
    pass
