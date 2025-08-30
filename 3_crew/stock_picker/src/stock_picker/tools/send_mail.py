# tools/send_mail.py
from typing import Type, List, Optional
from pydantic import BaseModel, Field, EmailStr
from crewai.tools import BaseTool
import os, smtplib, ssl
from email.message import EmailMessage


class SendMailInput(BaseModel):
    """พารามิเตอร์สำหรับส่งอีเมล"""

    to: List[EmailStr] = Field(..., description="อีเมลผู้รับ (หลายคนได้)")
    subject: str = Field(..., description="หัวข้ออีเมล")
    body: str = Field(..., description="ข้อความอีเมล (plain text)")
    cc: Optional[List[EmailStr]] = Field(default=None, description="รายชื่อ CC")
    bcc: Optional[List[EmailStr]] = Field(default=None, description="รายชื่อ BCC")


class SendMailTool(BaseTool):
    name: str = "send_mail"
    description: str = (
        "ส่งอีเมลผ่าน SMTP โดยอ่าน ENV: "
        "SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD, SMTP_FROM"
    )
    args_schema: Type[BaseModel] = SendMailInput

    def _run(
        self,
        to: List[str],
        subject: str,
        body: str,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
    ) -> str:
        host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        port = int(os.getenv("SMTP_PORT", "587"))
        username = os.getenv("SMTP_USERNAME")
        password = os.getenv("SMTP_PASSWORD")
        sender = os.getenv("SMTP_FROM", username)
        
        print(f"body: {body}")

        if not username or not password or not sender:
            return '{"status":"error","message":"SMTP env not set"}'

        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = ", ".join(to)
        if cc:
            msg["Cc"] = ", ".join(cc)
        msg["Subject"] = subject
        msg.set_content(body)

        recipients = to + (cc or []) + (bcc or [])

        context = ssl.create_default_context()
        with smtplib.SMTP(host, port) as server:
            server.starttls(context=context)
            server.login(username, password)
            server.send_message(msg=msg, from_addr=sender, to_addrs=recipients)

        return f'{{"status":"ok","sent":{len(recipients)}}}'
