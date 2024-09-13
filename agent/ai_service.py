import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import UserMessage
from azure.ai.inference.models import SystemMessage
from azure.core.credentials import AzureKeyCredential
from composio_openai import ComposioToolSet, App, Action
from datetime import datetime
import pytz
from typing import Any, List
from .google_fit_service import GoogleFitService
from dotenv import load_dotenv
from .exceptions import ServiceException

load_dotenv()

class HealthAgentService:

    __composio_toolset = ComposioToolSet()
    _instance = None
    __pat = os.getenv("GITHUB_TOKEN")

    def __init__(self, headers: dict, client_email: str):
        self.headers = headers
        self.client_email = client_email
        self.__fitness_service = GoogleFitService(headers=self.headers)

    # list of actions

    # insight base on weight and height
    def get_weight_height_insight(self) -> Any:
        weight_height = self.__fitness_service.get_weight_height_val()
        height = weight_height["height"]
        weight = weight_height["weight"]
        if weight <= 0 or height <= 0:
            raise ServiceException(
                "You must update your weight and height on the google fit app",
                status_code=400,
            )
        tools = self.__composio_toolset.get_tools(actions=[Action.GMAIL_SEND_EMAIL])
        task = f"Send health reccommendation tips email for a person with height:{height} and weight:{weight} as a body with the following data to:{self.client_email}, subject:Health related quoute"
        res = self.__ai_service(task, tools)
        result = self.__composio_toolset.handle_tool_calls(res)
        print(result)
        return result

    # ensuring the service object is singleton
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __ai_service(self, task, tools: Any = None):
        """Handles third party ai services"""

        print(f"This is pat {self.__pat} from ai service")

        client = ChatCompletionsClient(
            endpoint="https://models.inference.ai.azure.com",
            credential=AzureKeyCredential(f"{self.__pat}"),
        )

        response = None

        if tools:
            response = client.complete(
                messages=[
                    SystemMessage(content="You are a helpful assistant."),
                    UserMessage(content=task),
                ],
                tools=tools,
                model="gpt-4o",
                temperature=0.8,
                max_tokens=4096,
                top_p=0.1,
            )
        else:
            response = client.complete(
                messages=[
                    SystemMessage(content="You are a helpful assistant."),
                    UserMessage(content=task),
                ],
                model="gpt-4o",
                temperature=0.8,
                max_tokens=4096,
                top_p=0.1,
            )
        return response
