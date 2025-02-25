import random
import string
from datetime import timedelta
from typing import Optional

from django.template.loader import render_to_string
from django.utils import timezone
from sms import Message

from .models import SMSVerification


class DefaultSMSVerificationHandler:
    """
    Production-ready store for SMS verification codes using database persistence.
    """
    CODE_LENGTH = 6
    CODE_CHARS = string.digits  # Only use numbers for verification codes
    CODE_EXPIRY_MINUTES = 10

    @classmethod
    def create_verification(cls, phone_number: str, code: Optional[str] = None) -> SMSVerification:
        """
        Create a new verification code for the given phone number.
        Returns the generated code.
        """
        # Generate random verification code
        code = code or ''.join(random.choices(cls.CODE_CHARS, k=cls.CODE_LENGTH))

        # Delete any existing unverified codes for this number
        SMSVerification.objects.filter(
            phone_number=phone_number,
            verified=False
        ).delete()

        # Create new verification record
        sms_verification = SMSVerification.objects.create(
            phone_number=phone_number,
            code=code,
            verified=False
        )
        context = {
            "code": sms_verification.code
        }

        content = render_to_string(f"sms/sms_content.txt", context)

        msg = Message(
            content,
            None,
            [sms_verification.phone_number]
        )

        if not msg.send():
            raise Exception("Failed to send verification code")

        return sms_verification


    @classmethod
    def verify_code(cls, verification_id: str, code: str) -> Optional[SMSVerification]:
        """
        Verify the code for the given verification_id.
        Returns True if verification successful, False otherwise.
        """
        # Calculate expiry cutoff time
        expiry_cutoff = timezone.now() - timedelta(minutes=cls.CODE_EXPIRY_MINUTES)

        try:
            verification = SMSVerification.objects.get(
                id=verification_id,
                code=code,
                verified=False,
                created_at__gt=expiry_cutoff
            )
            # Mark as verified
            verification.verified = True
            verification.save()
            return verification

        except SMSVerification.DoesNotExist:
            return None

    @classmethod
    def cleanup_expired(cls):
        """
        Delete expired verification records.
        Can be run periodically via management command or celery task.
        """
        expiry_cutoff = timezone.now() - timedelta(minutes=cls.CODE_EXPIRY_MINUTES)
        SMSVerification.objects.filter(created_at__lt=expiry_cutoff).delete()
