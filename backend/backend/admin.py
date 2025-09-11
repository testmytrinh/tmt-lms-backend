from courses.queries import get_active_classes, get_active_open_classes
from enrollment.queries import get_all_enrollments, get_enrollments_this_month
from user.queries import get_all_users, get_active_users


def dashboard_callback(request, context):
    sum_active_classes = get_active_classes().count()
    sum_active_open_classes = get_active_open_classes().count()

    sum_users = get_all_users().count()
    sum_active_users = get_active_users().count()

    sum_enrollments = get_all_enrollments().count()
    sum_new_enrollments_this_month = get_enrollments_this_month().count()


    context.update(
        {
            "user": request.user,
            "sum_active_classes": sum_active_classes,
            "sum_active_open_classes": sum_active_open_classes,
            "sum_users": sum_users,
            "sum_active_users": sum_active_users,
            "sum_enrollments": sum_enrollments,
            "sum_new_enrollments_this_month": sum_new_enrollments_this_month,
        }
    )

    return context
