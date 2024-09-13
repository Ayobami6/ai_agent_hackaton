from django.shortcuts import render
from rest_framework.views import APIView
from sparky_utils.response import service_response
from sparky_utils.exceptions import handle_internal_server_exception
from .ai_service import HealthAgentService
from .exceptions import ServiceException

# Create your views here.


class RootPage(APIView):

    def get(self, request, *args, **kwargs):
        return service_response(
            status="success",
            message="Welcome to the AI Agent API",
            status_code=200,
        )


class AIAgentAPIView(APIView):
    """AI agent api view handler"""

    def get(self, request, *args, **kwargs):
        """get http request handler"""
        try:
            # get http request header to check authorization
            authorization = request.META.get("HTTP_AUTHORIZATION")
            if not authorization:
                return service_response(
                    status="error", message="Unauthorized", status_code=401
                )
            headers = {"Authorization": authorization}
            client_email = request.data.get("email")
            # create an instance of HealthAgentService
            agent = HealthAgentService(headers=headers, client_email=client_email)
            action = request.data.get("action")
            response = None
            # TODO: call AI service based on the action and client_email
            match action:
                case "weight_height":
                    _ = agent.get_weight_height_insight()
                    response = "An email as containing expert recommendations has been sent to your email"
                case _:
                    return service_response(
                        status="error",
                        message="Invalid action",
                        status_code=400,
                    )
            return service_response(status="success", message=response, status_code=200)

        except ServiceException as e:
            return service_response(status="error", message=(str(e)), status_code=400)
        except Exception:
            return handle_internal_server_exception()
