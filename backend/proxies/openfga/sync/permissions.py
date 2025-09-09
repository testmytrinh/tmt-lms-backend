from rest_framework.permissions import BasePermission
from abc import ABC, abstractmethod, ABCMeta

from . import client
from openfga_sdk.client.models import ClientCheckRequest

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
        req = ClientCheckRequest(tuple_key={
            "user": f"{self.subject_type}:{self.get_subject_id(request, view, obj)}",
            "relation": self.relation,
            "object": f"{self.object_type}:{self.get_object_id(request, view, obj)}",
        })
        resp = client.check(req)
        return bool(getattr(resp, "allowed", False))
