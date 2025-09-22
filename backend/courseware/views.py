from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from .permissions import (
    UserCanCreateClassNodes,
    UserCanListClasssNodes,
    UserCanViewContentNode,
    UserCanEditContentNode,
    UserCanModifyContentNode,
)
from .serializers import (
    ContentNodeListSerializer,
    ContentNodeDetailSerializer,
    ContentNodeWriteSerializer,
    ContentNodeTreeSerializer,
)
from . import queries


class ContentNodeViewSet(viewsets.ModelViewSet):
    PERMISSION_MAP = {
        "list": [UserCanListClasssNodes],
        "retrieve": [UserCanViewContentNode],
        "create": [UserCanCreateClassNodes],
        "update": [UserCanEditContentNode],
        "partial_update": [UserCanEditContentNode],
        "destroy": [UserCanModifyContentNode],
        "tree": [UserCanListClasssNodes],
    }
    SERIALIZER_MAP = {
        "list": ContentNodeListSerializer,
        "retrieve": ContentNodeDetailSerializer,
        "create": ContentNodeWriteSerializer,
        "update": ContentNodeWriteSerializer,
        "partial_update": ContentNodeWriteSerializer,
        "destroy": ContentNodeWriteSerializer,
        "tree": ContentNodeTreeSerializer,
    }

    def get_queryset(self):
        class_id = self.kwargs.get("class_id")
        return queries.get_nodes_by_class_id(class_id)

    def get_permissions(self):
        permission_classes = self.PERMISSION_MAP[self.action]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        return self.SERIALIZER_MAP[self.action]

    @action(detail=False, methods=["get"])
    def tree(self, request, *args, **kwargs):
        queryset = queries.get_root_nodes_by_class_id(
            self.kwargs.get("class_id")
        ).prefetch_related("children")
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
