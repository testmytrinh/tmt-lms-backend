from rest_framework import viewsets

from .models import Department, Term
from .serializers import DepartmentSerializer, TermSerializer


class DepartmentViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.RetrieveModelMixin,
):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()


class TermViewSet(
    viewsets.GenericViewSet,
    viewsets.mixins.ListModelMixin,
    viewsets.mixins.RetrieveModelMixin,
):
    serializer_class = TermSerializer
    queryset = Term.objects.all()
