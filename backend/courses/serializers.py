from rest_framework import serializers

from user.serializers import UserReadSerializer
from enrollment import queries

from .models import Course, CourseCategory, CourseClass


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
        return queries.count_course_class_enrollments(obj.id)

    def get_teachers(self, obj):
        teacher_enrollments = queries.get_course_class_teachers_enrollment(
            obj.id
        ).select_related("user")
        return UserReadSerializer([e.user for e in teacher_enrollments], many=True).data


class CourseClassWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseClass
        fields = "__all__"
