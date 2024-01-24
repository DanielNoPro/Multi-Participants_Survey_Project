from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.viewsets import GenericViewSet


class WriteOnlyModelViewSet(CreateModelMixin, UpdateModelMixin, DestroyModelMixin, GenericViewSet):
    pass
