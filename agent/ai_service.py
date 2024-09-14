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
        if int(weight) <= 0 or int(height) <= 0:
            raise ServiceException(
                "You must update your weight and height on the google fit app",
                status_code=400,
            )
        tools = self.__composio_toolset.get_tools(
            actions=[Action.GMAIL_SEND_EMAIL])
        task = f"Send health recommendations tips email for a person with height:{height} and weight:{
            weight} as a body with the following data to:{self.client_email}, subject:Health related quoute"
        res = self.__ai_service(task, tools)
        result = self.__composio_toolset.handle_tool_calls(res)
        print(result)
        return result

    def fat_insight(self):
        """Get AI Insight base on your body fat"""
        body_fat = self.__fitness_service.get_body_fat_val()
        if int(body_fat) <= 0:
            raise ServiceException(
                "You must update your weight on the google fit app",
                status_code=400,
            )
        task = f"Give me health recommendations base on my body fat{body_fat}"
        res = self.__ai_service(task)
        result = res.choices[0].message.content
        return result

    def ask_anything(self, task):
        """Ask anything from the ai agent"""
        response = self.__ai_service(task)
        result = response.choices[0].message.content
        return result

    def bp_insight(self) -> str:
        """Get AI Agent insight and health recommendation on blood pressure level"""
        bp, numerator, denom = self.__fitness_service.get_bp_data()
        if int(numerator) <= 0 or int(denom) <= 0:
            raise ServiceException(
                "You must update your blood pressure on the google fit app",
                status_code=400,
            )
        task: str = f"""Based on the blood pressure
        {bp} provided give a physician recommendations on management and cure if above standard threshold or recommendations to maintain and stay healthy if normal. Also don't fail to mention some common side effects of high blood pressure if the blood pressure is too low or too high"""
        response = self.__ai_service(task)
        result = response.choices[0].message.content
        return result

    def general_insight(self) -> Any:
        """Get general insight based fitness data
        """
        data = self.__fitness_service.get_data()
        print(data)
        tools = self.__composio_toolset.get_tools(
            actions=[Action.GMAIL_SEND_EMAIL])
        task = f"""Send health recommendations email for a general health check with this health data \
        {data} to: {self.client_email}subject: General health check"""
        res = self.__ai_service(task, tools)
        result = self.__composio_toolset.handle_tool_calls(res)
        return result

    def create_workout_event(self) -> Any:
        """Creates a google calendar workout event
        """
        weight_height = self.__fitness_service.get_weight_height_val()
        height = weight_height["height"]
        weight = weight_height["weight"]
        if int(weight) <= 0 or int(height) <= 0:
            raise ServiceException(
                "You must update your weight and height on the google fit app",
                status_code=400,
            )
        fat = self.__fitness_service.get_body_fat_val()
        tools = self.__composio_toolset.get_tools(
            actions=[Action.GOOGLECALENDAR_CREATE_EVENT])
        current_time = datetime.now(pytz.timezone('UTC')).astimezone()

        current_timezone = current_time.tzname()
        print(current_time, current_timezone)
        # task = f"""create a one week 30mins workout event in my google calendar on this email:ayobamidele006@gmail.com with a summary of what kind of workout activity you recommend base on my height:{height}\
        #     and weight{weight} from my current time:{current_time} with timezone:{current_timezone}"""
        task = f"""create a one week 30mins workout event in my google calendar on this email:{self.client_email} with a summary of what kind of workout activity you recommend base on height:{height} and weight:{weight} from current
        time:{current_time} with timezone:{current_timezone}"""
        res = self.__ai_service(task, tools)
        result = self.__composio_toolset.handle_tool_calls(res)
        return result

    # ensuring the service object is singleton
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __ai_service(self, task, tools: Any = None):
        """Handles third party ai services"""

        client = ChatCompletionsClient(
            endpoint="https://models.inference.ai.azure.com",
            credential=AzureKeyCredential(f"{self.__pat}"),
        )

        response = None

        if tools:
            print("called")
            response = client.complete(
                messages=[
                    SystemMessage(
                        content="You are a helpful assistant."),
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
                    SystemMessage(
                        content="You are a helpful health physician."),
                    UserMessage(content=task),
                ],
                model="gpt-4o",
                temperature=0.8,
                max_tokens=4096,
                top_p=0.1,
            )
        return response
