from django.db.models import Q, Exists, OuterRef

from .models import (
    Course,
    CourseCategory,
    CourseClass,
    CourseTemplate,
    Module,
    Enrollment,
    Lesson,
    StudyGroup,
)

def get_all_course_categories():
    return CourseCategory.objects.all()

def get_all_courses():
    return Course.objects.all()
    

def get_all_classes():
    return CourseClass.objects.all()


def get_active_open_classes():
    return CourseClass.objects.filter(is_active=True, is_open=True)


def get_visible_classes(user):
    if user.has_perm("courses.view_courseclass"):
        return CourseClass.objects.all()
    return CourseClass.objects.filter(
        Q(is_open=True)
        | Exists(Enrollment.objects.filter(course_class=OuterRef("pk"), user=user))
    )


def get_user_classes(user):
    return CourseClass.objects.filter(enrollments__user=user)

def get_no_classes():
    return CourseClass.objects.none()