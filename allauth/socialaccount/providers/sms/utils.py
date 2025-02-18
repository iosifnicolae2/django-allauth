import random
import time
from datetime import datetime, timedelta
from typing import Optional

from django.conf import settings
from django.template.loader import render_to_string

from .message import Message


class SMSVerification:
    def __init__(self, id: str, phone_number: str, code: str, created_at: float):
        self.id = id
        self.phone_number = phone_number
        self.code = code
        self.created_at = created_at

    def is_expired(self) -> bool:
        expiry_minutes = settings.SOCIALACCOUNT_PROVIDERS['sms'].get('CODE_EXPIRY', 10)
        expiry_time = self.created_at + (expiry_minutes * 60)
        return time.time() > expiry_time

    def verify(self, code: str) -> bool:
        if self.is_expired():
            return False
        return self.code == code

    def send(self) -> bool:
        template_prefix = "sms"
        context = {
            "code": self.code
        }
        
        content = render_to_string(f"{template_prefix}/sms_content.txt", context)
        
        return Message(
            content=content,
            from_phone=settings.SOCIALACCOUNT_PROVIDERS['sms']['FROM_NUMBER'],
            to_phone=self.phone_number
        ).send()


class SMSVerificationStore:
    """
    A simple in-memory store for SMS verifications.
    In production, you'd want to use a proper database or cache backend.
    """
    _verifications = {}

    def create_verification(self, phone_number: str) -> SMSVerification:
        # Generate random verification code
        code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Generate random ID for the verification
        id = str(random.getrandbits(32))
        
        verification = SMSVerification(
            id=id,
            phone_number=phone_number,
            code=code,
            created_at=time.time()
        )
        
        self._verifications[id] = verification
        return verification

    def get_verification(self, id: str) -> Optional[SMSVerification]:
        verification = self._verifications.get(id)
        if verification and verification.is_expired():
            self.remove_verification(id)
            return None
        return verification

    def remove_verification(self, id: str) -> None:
        self._verifications.pop(id, None)
