# tools/send_mail.py
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import os, smtplib, ssl, socket
from email.message import EmailMessage

# ---- ค่าคงที่ผู้รับ/หัวข้อ ----
FIXED_TO = ["luecha.kanm@gmail.com"]
FIXED_CC = []
FIXED_BCC = []
DEFAULT_SUBJECT = "Stock Picker Notification"


class SendMailInput(BaseModel):
    mes: str = Field(..., description="ข้อความอีเมล; บรรทัดแรกใส่ 'Subject: ...' ได้")


class SendMailTool(BaseTool):
    name: str = "send_mail"
    description: str = (
        "ส่งอีเมลผ่าน SMTP โดยอ่าน ENV: SMTP_HOST, SMTP_PORT, SMTP_USERNAME, "
        "SMTP_PASSWORD, SMTP_FROM"
    )
    args_schema: Type[BaseModel] = SendMailInput

    def _run(self, mes: str) -> str:
        host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
        port: int = int(os.getenv("SMTP_PORT", "587"))
        username: str | None = os.getenv("SMTP_USERNAME")
        password: str | None = os.getenv("SMTP_PASSWORD")
        sender: str | None = os.getenv("SMTP_FROM", username)

        if not (username and password and sender):
            return '{"status":"error","code":"env_missing","msg":"SMTP_USERNAME/PASSWORD/FROM not set"}'

        # แยก Subject จากบรรทัดแรกถ้ามี
        subject, body = DEFAULT_SUBJECT, mes
        lines: list[str] = mes.splitlines()
        if lines and lines[0].lower().startswith("subject:"):
            subject = lines[0][8:].strip() or DEFAULT_SUBJECT
            body: str = "\n".join(lines[1:]).lstrip("\n") or "(no content)"
        subject: str = " ".join(subject.splitlines())[:180]

        # สร้างข้อความ
        msg = EmailMessage()
        msg["From"] = sender
        msg["To"] = ", ".join(FIXED_TO)
        if FIXED_CC:
            msg["Cc"] = ", ".join(FIXED_CC)
        msg["Subject"] = subject
        msg.set_content(body)

        recipients: list[str] = FIXED_TO + FIXED_CC + FIXED_BCC

        try:
            if port == 465:
                with smtplib.SMTP_SSL(
                    host, port, context=ssl.create_default_context(), timeout=20
                ) as s:
                    s.login(username, password)
                    refused = s.send_message(msg, from_addr=sender, to_addrs=recipients)
            else:
                with smtplib.SMTP(host, port, timeout=20) as s:
                    s.ehlo()
                    s.starttls(context=ssl.create_default_context())
                    s.ehlo()
                    s.login(username, password)
                    refused = s.send_message(msg, from_addr=sender, to_addrs=recipients)
        except smtplib.SMTPAuthenticationError as e:
            return f'{{"status":"error","code":"auth","msg":"{e}"}}'
        except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected) as e:
            return f'{{"status":"error","code":"connect","msg":"{e}"}}'
        except (socket.gaierror, TimeoutError) as e:
            return f'{{"status":"error","code":"network","msg":"{e}"}}'
        except Exception as e:
            return (
                f'{{"status":"error","code":"unknown","msg":"{type(e).__name__}: {e}"}}'
            )

        if isinstance(refused, dict) and refused:
            return f'{{"status":"partial_fail","refused":{list(refused.keys())}}}'

        return f'{{"status":"ok","sent":{len(recipients)}}}'
