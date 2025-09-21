"""
OpenFGA operation decorators for consistent logging and error handling
"""
import logging
import functools
from typing import Callable
import time

logger = logging.getLogger(__name__)


def log_operation(operation_name: str = None, log_level: int = logging.INFO):
    """
    Decorator to log operation start, success, and errors

    Args:
        operation_name: Custom operation name for logging (defaults to function name)
        log_level: Logging level for success messages
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__
            start_time = time.time()

            try:
                logger.debug(f"Starting {op_name}")
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                logger.log(log_level, f"Completed {op_name} in {duration:.3f}s")
                return result

            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Failed {op_name} after {duration:.3f}s: {e}")
                raise

        return wrapper
    return decorator


def log_sync_operation(sync_type: str):
    """
    Decorator specifically for sync operations that log the number of items processed

    Args:
        sync_type: Type of sync operation (e.g., 'user_groups', 'enrollments')
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                logger.debug(f"Starting {sync_type} sync")
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                # Try to extract count from result or arguments
                count = 0
                if hasattr(result, '__len__'):
                    count = len(result)
                elif len(args) > 0 and hasattr(args[0], '__len__'):
                    count = len(args[0])
                elif len(args) > 1 and hasattr(args[1], '__len__'):
                    count = len(args[1])

                logger.info(f"Synced {count} {sync_type} in {duration:.3f}s")
                return result

            except Exception as e:
                duration = time.time() - start_time
                logger.error(f"Failed {sync_type} sync after {duration:.3f}s: {e}")
                raise

        return wrapper
    return decorator


def log_tuple_operation(operation: str):
    """
    Decorator for tuple operations that logs tuple details on failure

    Args:
        operation: Operation type (e.g., 'write', 'delete', 'check')
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                logger.debug(f"Successfully {operation}d tuples")
                return result

            except Exception as e:
                # Log tuple details for debugging
                if args:
                    for i, arg in enumerate(args):
                        if hasattr(arg, '__iter__') and not isinstance(arg, str):
                            logger.error(f"Failed {operation} tuples - arg {i}: {list(arg)[:3]}...")
                        else:
                            logger.error(f"Failed {operation} tuples - arg {i}: {arg}")
                logger.error(f"Failed to {operation} tuples: {e}")
                raise

        return wrapper
    return decorator


def log_check_operation():
    """
    Decorator for check operations that logs the result
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                # Extract identifiers from args for logging
                identifiers = []
                if len(args) >= 3:  # file_id, user_id, relation
                    identifiers = [str(args[0]), str(args[1]), args[2]]

                logger.debug(f"Permission check result: {result} for {identifiers}")
                return result

            except Exception as e:
                logger.error(f"Permission check failed: {e}")
                raise

        return wrapper
    return decorator


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """
    Decorator to retry operations on failure

    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"Attempt {attempt + 1} failed, retrying: {e}")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} attempts failed: {e}")

            raise last_exception

        return wrapper
    return decorator


def handle_openfga_errors(operation_name: str = None):
    """
    Decorator to handle OpenFGA-specific errors with appropriate logging

    Args:
        operation_name: Custom operation name for logging
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__

            try:
                return func(*args, **kwargs)

            except Exception as e:
                error_type = type(e).__name__

                # Handle specific OpenFGA error types
                if "OpenFGA" in error_type or "Client" in error_type:
                    logger.error(f"OpenFGA client error in {op_name}: {e}")
                elif "Network" in error_type or "Connection" in error_type:
                    logger.error(f"Network error in {op_name}: {e}")
                elif "Timeout" in error_type:
                    logger.error(f"Timeout error in {op_name}: {e}")
                else:
                    logger.error(f"Unexpected error in {op_name}: {e}")

                raise

        return wrapper
    return decorator


def signal_handler(operation_name: str = None, silent: bool = False):
    """
    Decorator for Django signal handlers with automatic error handling

    Args:
        operation_name: Custom operation name for logging
        silent: If True, don't log successful operations (only errors)
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__

            try:
                result = func(*args, **kwargs)
                if not silent:
                    logger.debug(f"Signal {op_name} completed successfully")
                return result

            except Exception as e:
                logger.error(f"Signal {op_name} failed: {e}")
                # Don't re-raise - signals should fail silently to not break model saves
                return None

        return wrapper
    return decorator


def sync_signal(operation_name: str = None):
    """
    Decorator for sync-related signal handlers

    Args:
        operation_name: Custom operation name for logging
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or func.__name__

            try:
                result = func(*args, **kwargs)
                logger.info(f"Sync signal {op_name} completed")
                return result

            except Exception as e:
                logger.error(f"Sync signal {op_name} failed: {e}")
                # Don't re-raise - signals should fail silently
                return None

        return wrapper
    return decorator