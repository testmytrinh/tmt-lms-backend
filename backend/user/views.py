from django.http import HttpRequest
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class UserView(APIView):
    """
    User view to handle user-related operations.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request: HttpRequest):
        """
        Handle GET requests to retrieve user information.
        """
        # Logic to retrieve user information goes here
        return Response({"message": request.user.email})