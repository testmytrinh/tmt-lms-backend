import functools
import logging

logger = logging.getLogger(__name__)


def handle_course_class_presave_syncing_exceptions(func):
    @functools.wraps(func)
    def wrapper(sender, instance, raw, using, update_fields, **kwargs):
        try:
            return func(sender, instance, raw, using, update_fields, **kwargs)
        except Exception as e:
            logger.error(
                f"An exception occurred in signal '{func.__name__}' "
                f"for class '{instance.name}' (ID: {instance.id}):\n"
                f"{e}",
                exc_info=True,
            )
            # Re-raise the exception to prevent silent failures
            raise

    return wrapper

def handle_course_class_postsave_syncing_exceptions(func):
    @functools.wraps(func)
    def wrapper(sender, instance, created, **kwargs):
        try:
            return func(sender, instance, created, **kwargs)
        except Exception as e:
            logger.error(
                f"An exception occurred in signal '{func.__name__}' "
                f"for class '{instance.name}' (ID: {instance.id}):\n"
                f"{e}",
                exc_info=True,
            )
            # Re-raise the exception to prevent silent failures
            raise

    return wrapper