from .models import Lesson, Module, ContentNode


def get_all_lessons():
    return Lesson.objects.all()


def get_all_modules():
    return Module.objects.all()


def get_nodes_by_class_id(class_id):
    return ContentNode.objects.filter(course_class_id=class_id)


def get_root_nodes_by_class_id(class_id):
    return ContentNode.objects.filter(
        course_class_id=class_id, parent__isnull=True
    ).order_by("order")
