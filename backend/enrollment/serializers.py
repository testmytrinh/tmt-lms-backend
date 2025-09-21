from dataclasses import dataclass, field, asdict, InitVar
from rest_framework import serializers

from services.openfga.sync.utils import filter_allowed_relations
from services.openfga.relations import CourseClassRelation, UserRelation
from user.serializers import UserReadSerializer

from .models import Enrollment, EnrollmentRole, StudyGroup


@dataclass
class CourseClassAccess:
    enrollment: InitVar[Enrollment]
    can_view: bool = field(init=False, default=False)
    can_edit: bool = field(init=False, default=False)

    def __post_init__(self, enrollment: Enrollment):
        allowed_relations = filter_allowed_relations(
            subject_key=f"{UserRelation.TYPE}:{enrollment.user.pk}",
            object_key=f"{CourseClassRelation.TYPE}:{enrollment.course_class.pk}",
            relations=[CourseClassRelation.CAN_VIEW, CourseClassRelation.CAN_EDIT],
        )
        self.can_edit = CourseClassRelation.CAN_EDIT in allowed_relations
        self.can_view = CourseClassRelation.CAN_VIEW in allowed_relations


class EnrollmentReadSerializer(serializers.ModelSerializer):
    user = UserReadSerializer(read_only=True)
    role = serializers.CharField(source="get_role_display")
    access = serializers.SerializerMethodField()

    class Meta:
        model = Enrollment
        fields = "__all__"

    def get_access(self, obj):
        return asdict(CourseClassAccess(enrollment=obj))


class EnrollmentWriteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    role = serializers.HiddenField(default=EnrollmentRole.GUEST)

    class Meta:
        model = Enrollment
        fields = "__all__"

    def validate_course_class(self, value):
        if not value.is_open:
            raise serializers.ValidationError("This course class is not valid.")
        return value


class StudyGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyGroup
        fields = "__all__"
