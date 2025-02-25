from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class SMSVerification(models.Model):
    phone_number = PhoneNumberField()
    code = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    verified = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['phone_number', 'code'], name='sms_verification_lookup'),
        ]
