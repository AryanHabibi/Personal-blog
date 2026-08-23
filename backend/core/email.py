import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import settings


def send_verification_email(to_email: str, token: str) -> None:
    verify_link = f"{settings.app_base_url}/users/verify?token={token}"

    if settings.environment == "development":
        print(f"[DEV] Verification link for {to_email}: {verify_link}")

    message = MIMEMultipart("alternative")
    message["Subject"] = "Verify your Weblog account"
    message["From"] = settings.smtp_from_email
    message["To"] = to_email

    text_body = f"Click the link below to verify your email:\n{verify_link}"
    html_body = f'<p>Click the link below to verify your email:</p><p><a href="{verify_link}">{verify_link}</a></p>'
    message.attach(MIMEText(text_body, "plain"))
    message.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_username, settings.smtp_password)
        server.sendmail(settings.smtp_from_email, to_email, message.as_string())
