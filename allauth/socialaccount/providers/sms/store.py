import random
import string
from datetime import timedelta

from django.utils import timezone

from .models import SMSVerification


class SMSVerificationStore:
    """
    Production-ready store for SMS verification codes using database persistence.
    """
    CODE_LENGTH = 6
    CODE_CHARS = string.digits  # Only use numbers for verification codes
    CODE_EXPIRY_MINUTES = 10

    @classmethod
    def create_verification(cls, phone_number: str) -> str:
        """
        Create a new verification code for the given phone number.
        Returns the generated code.
        """
        # Generate random verification code
        code = ''.join(random.choices(cls.CODE_CHARS, k=cls.CODE_LENGTH))
        
        # Delete any existing unverified codes for this number
        SMSVerification.objects.filter(
            phone_number=phone_number,
            verified=False
        ).delete()
        
        # Create new verification record
        SMSVerification.objects.create(
            phone_number=phone_number,
            code=code,
            verified=False
        )
        
        return code

    @classmethod
    def verify_code(cls, phone_number: str, code: str) -> bool:
        """
        Verify the code for the given phone number.
        Returns True if verification successful, False otherwise.
        """
        # Calculate expiry cutoff time
        expiry_cutoff = timezone.now() - timedelta(minutes=cls.CODE_EXPIRY_MINUTES)
        
        try:
            verification = SMSVerification.objects.get(
                phone_number=phone_number,
                code=code,
                verified=False,
                created_at__gt=expiry_cutoff
            )
            # Mark as verified
            verification.verified = True
            verification.save()
            return True
            
        except SMSVerification.DoesNotExist:
            return False

    @classmethod
    def cleanup_expired(cls):
        """
        Delete expired verification records.
        Can be run periodically via management command or celery task.
        """
        expiry_cutoff = timezone.now() - timedelta(minutes=cls.CODE_EXPIRY_MINUTES)
        SMSVerification.objects.filter(created_at__lt=expiry_cutoff).delete()
