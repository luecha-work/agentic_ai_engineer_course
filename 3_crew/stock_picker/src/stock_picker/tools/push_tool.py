from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import requests


class PushNotificationInput(BaseModel):
    """A message to be sent to the user"""
    message: str = Field(..., description="The message to be sent to the user")


class PushNotificationTool(BaseTool):
    name: str = "Sent a push notification"
    description: str = (
        "This tool is used to send a push notification to the user"
    )
    args_schema: Type[BaseModel] = PushNotificationInput

    def _run(self, mes: str) -> str:
        # Implementation goes here
        print(f"Push: {mes}")
        
        
        return '{"notification": "ok"}'
