from django.db import models
from django.utils import timezone

class SMSVerification(models.Model):
    phone_number = models.CharField(max_length=32)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    verified = models.BooleanField(default=False)
    
    class Meta:
        indexes = [
            models.Index(fields=['phone_number', 'code']),
        ]
