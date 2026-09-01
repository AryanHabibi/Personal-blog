import smtplib
import sys
import traceback
from email.message import EmailMessage

from app.config import get_settings

settings = get_settings()


def send_verification_email(to: str, first_name: str, link: str) -> None:
    """Send (console mode: print) the address-confirmation link.

    Failures are swallowed - a flaky mail server must not break registration;
    the user can always call /auth/verify-email/resend.
    """
    subject = "Confirm your email address"
    body = (
        f"Hi {first_name},\n\n"
        f"Confirm this email address by opening the link below:\n\n"
        f"{link}\n\n"
        f"It expires in {settings.verification_token_ttl_hours} hours. "
        f"If you didn't create an account you can ignore this message.\n"
    )
    try:
        if settings.email_backend == "smtp":
            _send_via_smtp(to, subject, body)
        else:
            print(
                f"\n===== verification email (console backend) =====\n"
                f"to:      {to}\n"
                f"subject: {subject}\n\n"
                f"{body}"
                f"===============================================\n",
                flush=True,
            )
    except Exception:  # noqa: BLE001 - never propagate a mail failure
        print(f"[mailer] could not send verification email to {to}:", file=sys.stderr)
        traceback.print_exc()


def _send_via_smtp(to: str, subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["From"] = settings.email_from
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
        if settings.smtp_tls:
            server.starttls()
        if settings.smtp_user:
            server.login(settings.smtp_user, settings.smtp_password or "")
        server.send_message(msg)
