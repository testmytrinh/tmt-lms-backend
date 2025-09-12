from rest_framework import viewsets

from . import queries
from .serializers import DepartmentSerializer, TermSerializer


class DepartmentViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.RetrieveModelMixin,
):
    serializer_class = DepartmentSerializer
    queryset = queries.get_all_departments()


class TermViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.RetrieveModelMixin,
):
    serializer_class = TermSerializer
    queryset = queries.get_all_terms()
