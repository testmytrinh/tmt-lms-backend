from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    DjangoModelPermissions,
    IsAdminUser,
)

from .permissions import (
    OFGAUserCanEditTemplate,
    OFGAUserCanViewTemplate,
    OFGAUserCanModifyTemplate,
    OFGAUserCanViewTemplateNodesInPath,
    OFGAUserCanModifyNode,
    OFGAUserCanViewNode,
    OFGAUserCanEditNode,
    OFGAUserCanEditLesson,
    OFGAUserCanViewLesson,
    OFGAUserCanEditModule,
    OFGAUserCanViewModule,
)
from .serializers import (
    CourseTemplateReadSerializer,
    CourseTemplateWriteSerializer,
    ModuleSerializer,
    LessonSerializer,
    TemplateNodeListSerializer,
    TemplateNodeDetailSerializer,
    TemplateNodeWriteSerializer,
)
from .pagination import StandardResultsSetPagination
from . import queries


class CourseTemplateViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    QUERYSET_MAP = {
        "list": lambda _: queries.get_all_course_templates(),
        "retrieve": lambda _: queries.get_all_course_templates(),
        "update": lambda _: queries.get_all_course_templates(),
        "partial_update": lambda _: queries.get_all_course_templates(),
        "destroy": lambda _: queries.get_all_course_templates(),
        "me": lambda req: queries.get_templates_by_owner(req.user),
    }
    PERMISSION_MAP = {
        "list": [IsAdminUser],
        "retrieve": [OFGAUserCanViewTemplate],
        "create": [DjangoModelPermissions],
        "update": [IsAuthenticated, DjangoModelPermissions | OFGAUserCanEditTemplate],
        "partial_update": [
            IsAuthenticated,
            DjangoModelPermissions | OFGAUserCanEditTemplate,
        ],
        "destroy": [
            IsAuthenticated,
            DjangoModelPermissions | OFGAUserCanModifyTemplate,
        ],
        "me": [IsAuthenticated],
    }
    SERIALIZER_MAP = {
        "list": CourseTemplateReadSerializer,
        "retrieve": CourseTemplateReadSerializer,
        "create": CourseTemplateWriteSerializer,
        "update": CourseTemplateWriteSerializer,
        "partial_update": CourseTemplateWriteSerializer,
        "destroy": CourseTemplateWriteSerializer,
        "me": CourseTemplateReadSerializer,
    }

    def get_queryset(self):
        return self.QUERYSET_MAP[self.action](self.request)

    def get_permissions(self):
        permission_classes = self.PERMISSION_MAP[self.action]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        return self.SERIALIZER_MAP[self.action]

    @action(detail=False, methods=["get"])
    def me(self, request):
        templates = self.get_queryset()
        page = self.paginate_queryset(templates)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class TemplateNodeViewSet(viewsets.ModelViewSet):
    QUERYSET_MAP = {
        "list": lambda template_id: queries.get_nodes_by_template_id(template_id),
        "retrieve": lambda template_id: queries.get_nodes_by_template_id(template_id),
        "update": lambda template_id: queries.get_nodes_by_template_id(template_id),
        "partial_update": lambda template_id: queries.get_nodes_by_template_id(
            template_id
        ),
        "destroy": lambda template_id: queries.get_nodes_by_template_id(template_id),
        "curri": lambda template_id: queries.get_root_nodes_by_template_id(template_id),
    }
    PERMISSION_MAP = {
        "list": [OFGAUserCanViewTemplateNodesInPath],
        "retrieve": [OFGAUserCanViewNode],
        "create": [DjangoModelPermissions],
        "update": [IsAuthenticated, DjangoModelPermissions | OFGAUserCanEditNode],
        "partial_update": [
            IsAuthenticated,
            DjangoModelPermissions | OFGAUserCanEditNode,
        ],
        "destroy": [
            IsAuthenticated,
            DjangoModelPermissions | OFGAUserCanModifyNode,
        ],
        "curri": [OFGAUserCanViewTemplateNodesInPath],
    }
    SERIALIZER_MAP = {
        "list": TemplateNodeListSerializer,
        "retrieve": TemplateNodeDetailSerializer,
        "create": TemplateNodeWriteSerializer,
        "update": TemplateNodeWriteSerializer,
        "partial_update": TemplateNodeWriteSerializer,
        "destroy": TemplateNodeWriteSerializer,
        "curri": TemplateNodeListSerializer,
    }

    def get_queryset(self):
        template_id = self.kwargs.get("template_id")
        return self.QUERYSET_MAP[self.action](template_id)

    def get_permissions(self):
        permission_classes = self.PERMISSION_MAP[self.action]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        return self.SERIALIZER_MAP[self.action]

    @action(detail=False, methods=["get"])
    def curri(self, request, template_id=None):
        nodes = self.get_queryset()
        serializer = self.get_serializer(nodes, many=True)
        return Response(serializer.data)


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = queries.get_all_modules()
    serializer_class = ModuleSerializer
    PERMISSION_MAP = {
        "list": [DjangoModelPermissions],
        "retrieve": [OFGAUserCanViewModule],
        "create": [DjangoModelPermissions],
        "update": [IsAuthenticated, DjangoModelPermissions | OFGAUserCanEditModule],
        "partial_update": [
            IsAuthenticated,
            DjangoModelPermissions | OFGAUserCanEditModule,
        ],
        "destroy": [
            IsAuthenticated,
            DjangoModelPermissions | OFGAUserCanModifyNode,
        ],
    }

    def get_permissions(self):
        permission_classes = self.PERMISSION_MAP[self.action]
        return [permission() for permission in permission_classes]


class LessonViewSet(viewsets.ModelViewSet):
    queryset = queries.get_all_lessons()
    serializer_class = LessonSerializer
    PERMISSION_MAP = {
        "list": [DjangoModelPermissions],
        "retrieve": [OFGAUserCanViewLesson],
        "create": [DjangoModelPermissions],
        "update": [IsAuthenticated, DjangoModelPermissions | OFGAUserCanEditLesson],
        "partial_update": [
            IsAuthenticated,
            DjangoModelPermissions | OFGAUserCanEditLesson,
        ],
        "destroy": [
            IsAuthenticated,
            DjangoModelPermissions | OFGAUserCanModifyNode,
        ],
    }
    def get_permissions(self):
        permission_classes = self.PERMISSION_MAP[self.action]
        return [permission() for permission in permission_classes]