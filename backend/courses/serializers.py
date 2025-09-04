from rest_framework import serializers
from django.contrib.auth import get_user_model

from user.serializers import UserReadSerializer

from .models import (
    Course,
    CourseCategory,
    CourseClass,
    CourseTemplate,
    Module,
    Enrollment,
    EnrollmentRole,
    Lesson,
    StudyGroup,
)

User = get_user_model()


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = "__all__"


class CourseClassReadSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    teachers = serializers.SerializerMethodField()
    enrollment_count = serializers.SerializerMethodField()

    class Meta:
        model = CourseClass
        fields = "__all__"

    def get_enrollment_count(self, obj):
        return obj.enrollments.exclude(role=EnrollmentRole.TEACHER).count()

    def get_teachers(self, obj):
        teacher_enrollments = obj.enrollments.filter(
            role=EnrollmentRole.TEACHER
        ).select_related("user")
        return UserReadSerializer([e.user for e in teacher_enrollments], many=True).data


class CourseClassWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseClass
        fields = "__all__"


class CourseTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseTemplate
        fields = "__all__"


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = "__all__"


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = "__all__"


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"


class StudyGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyGroup
        fields = "__all__"
