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


# from typing import Type, List
# from pydantic import BaseModel, Field, EmailStr
# from crewai.tools import BaseTool
# import os, base64
# from email.message import EmailMessage

# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build

# SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


# class GmailSendInput(BaseModel):
#     to: List[EmailStr] = Field(..., description="ผู้รับ (หลายคนได้)")
#     subject: str = Field(..., description="หัวข้อ")
#     body: str = Field(..., description="เนื้อความ (plain text)")
#     cc: List[EmailStr] = Field(default_factory=list)
#     bcc: List[EmailStr] = Field(default_factory=list)
#     from_addr: EmailStr | None = None  # ถ้าไม่ระบุจะใช้บัญชีที่ล็อกอิน


# class GmailSendTool(BaseTool):
#     name: str = "gmail_send"
#     description: str = "ส่งอีเมลผ่าน Gmail API (ต้องมี credentials.json/token.json)"
#     args_schema: Type[BaseModel] = GmailSendInput

#     def _get_service(self):
#         cred_path = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
#         token_path = os.getenv("GOOGLE_TOKEN_FILE", "token.json")
#         creds = None
#         if os.path.exists(token_path):
#             creds = Credentials.from_authorized_user_file(token_path, SCOPES)
#         if not creds or not creds.valid:
#             if creds and creds.expired and creds.refresh_token:
#                 creds.refresh(Request())  # type: ignore[name-defined]
#             else:
#                 flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
#                 creds = flow.run_local_server(port=0)
#             with open(token_path, "w") as f:
#                 f.write(creds.to_json())
#         return build("gmail", "v1", credentials=creds)

#     def _run(
#         self,
#         to: List[str],
#         subject: str,
#         body: str,
#         cc: List[str] = None,
#         bcc: List[str] = None,
#         from_addr: str | None = None,
#     ) -> str:
#         cc = cc or []
#         bcc = bcc or []
#         svc = self._get_service()

#         msg = EmailMessage()
#         if from_addr:
#             msg["From"] = from_addr
#         msg["To"] = ", ".join(to)
#         if cc:
#             msg["Cc"] = ", ".join(cc)
#         msg["Subject"] = subject
#         msg.set_content(body)

#         raw = base64.urlsafe_b64encode(msg.as_bytes()).decode("utf-8")
#         svc.users().messages().send(userId="me", body={"raw": raw}).execute()
#         return f"gmail sent to {len(to)+len(cc)+len(bcc)} recipient(s)"
