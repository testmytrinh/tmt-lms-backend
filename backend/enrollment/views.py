from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


from .models import Enrollment, StudyGroup
from .serializers import EnrollmentSerializer, StudyGroupSerializer


class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer


class StudyGroupViewSet(viewsets.ModelViewSet):
    queryset = StudyGroup.objects.all()
    serializer_class = StudyGroupSerializer