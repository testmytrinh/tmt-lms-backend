from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions

from .pagination import StandardResultsSetPagination
from .queries import get_all_enrollments
from .serializers import EnrollmentReadSerializer, EnrollmentWriteSerializer


class EnrollmentViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    QUERYSET_MAP = {
        "list": lambda req: get_all_enrollments(),
        "retrieve": lambda req: get_all_enrollments(),
        "create": lambda req: get_all_enrollments(),
        "update": lambda req: get_all_enrollments(),
        "partial_update": lambda req: get_all_enrollments(),
        "destroy": lambda req: get_all_enrollments(),
    }
    PERMISSION_MAP = {
        "list": [IsAuthenticated],
        "retrieve": [IsAuthenticated],
        "create": [IsAuthenticated],
        "update": [IsAuthenticated, DjangoModelPermissions],
        "partial_update": [IsAuthenticated, DjangoModelPermissions],
        "destroy": [IsAuthenticated, DjangoModelPermissions],
    }
    SERIALIZER_MAP = {
        "list": EnrollmentReadSerializer,
        "retrieve": EnrollmentReadSerializer,
        "create": EnrollmentWriteSerializer,
        "update": EnrollmentWriteSerializer,
        "partial_update": EnrollmentWriteSerializer,
        "destroy": EnrollmentWriteSerializer,
    }

    def get_queryset(self):
        return self.QUERYSET_MAP[self.action](self.request)

    def get_permissions(self):
        permission_classes = self.PERMISSION_MAP[self.action]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        return self.SERIALIZER_MAP[self.action]
