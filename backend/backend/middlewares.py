from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import exception_handler
from django.core.exceptions import ObjectDoesNotExist
from botocore.exceptions import ClientError
import logging
from django.forms import ValidationError

logger = logging.getLogger(__name__)


_EXCEPTION_MAPPING = {
    ValueError: {
        "status_code": status.HTTP_400_BAD_REQUEST,
        "message": "Invalid input.",
    },
    PermissionError: {
        "status_code": status.HTTP_403_FORBIDDEN,
        "message": "Permission denied.",
    },
    ClientError: {
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "message": "Storage service went wrong.",
    },
    ObjectDoesNotExist: {
        "status_code": status.HTTP_404_NOT_FOUND,
        "message": "Resource not found.",
    },
    ValidationError: {
        "status_code": status.HTTP_400_BAD_REQUEST,
        "message": "Data validation error.",
    },
}


# https://www.django-rest-framework.org/api-guide/exceptions/#custom-exception-handling
def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    if optional_response := exception_handler(exc, context):
        return optional_response

    # Get request details for logging
    request = context.get("request")
    view = context.get("view")
    view_name = view.__class__.__name__ if view else "Unknown View"

    # For unhandled exceptions, check our mapping
    exception_class = next(
        (clz for clz in _EXCEPTION_MAPPING if isinstance(exc, clz)), None
    )

    if not exception_class:
        # Log the exception with context
        logger.error(
            f"\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Unhandled exception ({type(exception_class).__name__}) in {view_name}: {exc}",
            exc_info=True,
            extra={"path": request.path if request else "Unknown Path"},
        )
        logger.error("======================================\n\n")
        return Response(
            {"detail": "An unexpected error occurred."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Handle known exceptions
    return Response(
        {"detail": str(exc) or _EXCEPTION_MAPPING[exception_class]["message"]},
        status=_EXCEPTION_MAPPING[exception_class]["status_code"],
    )
