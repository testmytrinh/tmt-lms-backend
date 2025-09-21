from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from celery import shared_task


def send_email(
    subject: str,
    body: str,
    recipient_list: list,
    fail_silently: bool = False,
    from_email: str = settings.EMAIL_HOST_USER,
    content_subtype: str = "html",
) -> int:
    """
    Send an email using Django's EmailMessage class.

    :param subject: Subject of the email
    :param body: Body of the email
    :param recipient_list: List of recipient email addresses
    :param fail_silently: Whether to suppress errors
    :param from_email: Sender's email address
    :return: Number of successfully sent emails
    """

    email = EmailMessage(subject, body, from_email, to=recipient_list)
    email.content_subtype = content_subtype
    return email.send(fail_silently=fail_silently)


@shared_task
def send_account_activation_email(url: str, user_data: dict):
    to_email = user_data.get("email")
    html_template = "account_activation_email.html"
    context = {
        "full_name": f"{user_data.get('first_name')} {user_data.get('last_name')}",
        "activation_link": url,
    }

    html_message = render_to_string(html_template, context)
    send_email(
        subject="Activate your account",
        body=html_message,
        recipient_list=[to_email],
    )

    return f"Sending account activation email to {to_email} ({url})"
