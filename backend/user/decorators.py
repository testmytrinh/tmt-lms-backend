import functools
import logging

logger = logging.getLogger(__name__)


def handle_user_postsave_syncing_exceptions(func):
    @functools.wraps(func)
    def wrapper(sender, instance, created, **kwargs):
        try:
            return func(sender, instance, created, **kwargs)
        except Exception as e:
            logger.error(
                f"An exception occurred in signal '{func.__name__}' "
                f"for user '{instance.email}' (ID: {instance.id}, created: {created}):\n"
                f"{e}",
                exc_info=True,
            )
            # Re-raise the exception to prevent silent failures
            raise

    return wrapper


def handle_user_m2m_changed_syncing_exceptions(func):
    @functools.wraps(func)
    def wrapper(sender, instance, action, reverse, model, pk_set, **kwargs):
        try:
            return func(sender, instance, action, reverse, model, pk_set, **kwargs)
        except Exception as e:
            logger.error(
                f"An exception occurred in signal '{func.__name__}' "
                f"for user '{instance.email}' (ID: {instance.id}, action: {action})\n"
                f"!!!!!!!!! model: {model}, pk_set: {pk_set}:\n"
                f"{e}",
                exc_info=True,
            )
            # Re-raise the exception to prevent silent failures
            raise

    return wrapper
