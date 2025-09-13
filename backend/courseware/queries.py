from .models import CourseTemplate, Lesson, Module, TemplateNode


def get_all_course_templates():
    return CourseTemplate.objects.all()


def get_course_template_by_id(template_id):
    return CourseTemplate.objects.get(id=template_id)


def get_all_lessons():
    return Lesson.objects.all()


def get_all_modules():
    return Module.objects.all()


def get_nodes_by_template_id(template_id):
    return TemplateNode.objects.filter(course_template_id=template_id)


def get_templates_by_owner(user):
    return CourseTemplate.objects.filter(owner=user)


def get_root_nodes_by_template_id(template_id):
    return TemplateNode.objects.filter(
        course_template_id=template_id, parent__isnull=True
    ).order_by("order")
