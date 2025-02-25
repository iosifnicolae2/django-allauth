import importlib

from allauth.socialaccount import app_settings
from allauth.socialaccount.providers.base import Provider, ProviderAccount


class SMSAccount(ProviderAccount):
    def to_str(self):
        return self.account.extra_data.get('phone_number', '')


class SMSProvider(Provider):
    id = 'sms'
    name = 'SMS'
    account_class = SMSAccount
    # uses_apps = False

    def get_login_url(self, request, **kwargs):
        from django.urls import reverse
        return reverse('sms_login')

    @staticmethod
    def get_sms_verification_handler():
        settings = app_settings.PROVIDERS.get(SMSProvider.id, {})
        handler_class_name = settings.get('SMS_VERIFICATION_HANDLER', 'allauth.socialaccount.providers.sms.handler.DefaultSMSVerificationHandler')
        def get_class_from_string(class_path):
            """Dynamically import and return a class from its full path as a string."""
            module_path, class_name = class_path.rsplit('.', 1)  # Split into module and class name
            module = importlib.import_module(module_path)  # Import module dynamically
            return getattr(module, class_name)  # Get class from module
        handler_class = get_class_from_string(handler_class_name)
        return handler_class()

    @property
    def sub_id(self) -> str:
        return self.id

    def extract_uid(self, data):
        return data['phone_number']

    def extract_common_fields(self, data):
        return dict(
            phone_number=data.get('phone_number'),
        )

    def extract_extra_data(self, data):
        return dict(
            phone_number=data.get('phone_number'),
        )


provider_classes = [SMSProvider]
