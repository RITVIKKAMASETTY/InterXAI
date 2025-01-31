import random
import string
from django.core.mail import send_mail
from django.conf import settings


def generate_verification_code():
    return ''.join(random.choices(string.digits, k=6))

def send_verification_email(email, code):
    subject = 'Your Verification Code'
    message = f'Your verification code is: {code}\nThis code will expire in 30 seconds.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
def send_reset_code_email(email, code):
    subject = 'Password Reset Verification Code'
    message = f'Your password reset code is: {code}\nThis code will expire in 30 seconds.'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
