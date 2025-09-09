from rest_framework import serializers
from django.contrib.auth import get_user_model

from user.serializers import UserReadSerializer
from enrollment.models import EnrollmentRole

from .models import Course, CourseCategory, CourseClass

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
