from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import exception_handler
from django.core.exceptions import ObjectDoesNotExist
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)


_EXCEPTION_MAPPING = {
    ValueError: {
        "status_code": status.HTTP_400_BAD_REQUEST,
        "message": "Invalid input.",
    },
    PermissionError: {
        "status_code": status.HTTP_400_BAD_REQUEST,
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
}


# https://www.django-rest-framework.org/api-guide/exceptions/#custom-exception-handling
def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    # Get request details for logging
    request = context.get("request")
    view = context.get("view")
    view_name = view.__class__.__name__ if view else "Unknown"

    # Log the exception with context
    logger.error(
        f"\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\nException in {view_name}: {exc}",
        exc_info=True,
        extra={"path": request.path if request else "Unknown"},
    )
    logger.error("======================================\n\n")

    # If DRF already handled it, format the response consistently
    if response is not None:
        return response

    # For unhandled exceptions, check our mapping
    for exception_class in _EXCEPTION_MAPPING:
        if isinstance(exc, exception_class):
            message = (
                str(exc) if str(exc) else _EXCEPTION_MAPPING[exception_class]["message"]
            )
            return Response(
                {"detail": message},
                status=_EXCEPTION_MAPPING[exception_class]["status_code"],
            )

    # If we got here, it's a truly unexpected exception
    logger.critical(f"Unhandled exception: {exc}", exc_info=True)
    return Response(
        {"detail": "An unexpected error occurred."},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
