from rest_framework.permissions import BasePermission
from openfga_sdk.client import ClientCheckRequest
from abc import ABC, abstractmethod, ABCMeta

from . import client

BasePermissionMeta = type(BasePermission)

class FGABasePermissionMeta(ABCMeta, BasePermissionMeta):
    pass

class FGABasePermission(BasePermission, ABC, metaclass=FGABasePermissionMeta):
    @property
    @abstractmethod
    def relation(self) -> str:
        pass

    @property
    @abstractmethod
    def subject_type(self) -> str:
        pass

    @property
    @abstractmethod
    def object_type(self) -> str:
        pass

    @abstractmethod
    def get_subject_id(self, request, view, obj) -> str:
        pass

    @abstractmethod
    def get_object_id(self, request, view, obj) -> str:
        pass

    def has_object_permission(self, request, view, obj):
        body = ClientCheckRequest(
            user=f"{self.subject_type}:{self.get_subject_id(request, view, obj)}",
            relation=self.relation,
            object=f"{self.object_type}:{self.get_object_id(request, view, obj)}",
        )
        response = client.check(body)
        print(response)
        print(type(response))
        print(response.allowed)
        print(type(response.allowed))
        return response.allowed
