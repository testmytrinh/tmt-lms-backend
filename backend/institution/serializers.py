from rest_framework import serializers

from .models import Department, Term


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ["id", "name", "code"]


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = ["id", "name", "start_date", "end_date"]
