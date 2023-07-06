from datetime import timedelta
from django.utils.timezone import now
from uuid import uuid4

from celery import shared_task

from users_app.models import User, EmailVerification


@shared_task
def send_verification_email(user_id):
    user = User.objects.get(id=user_id)
    user_uuid = uuid4()
    expiration_date = now() + timedelta(hours=48)
    record = EmailVerification.objects.create(user=user, uuid_code=user_uuid, expiration=expiration_date)
    record.send_verification_email()
    print(f'celery sent an email ({user.email})')
