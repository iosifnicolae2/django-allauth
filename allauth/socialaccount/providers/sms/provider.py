from allauth.socialaccount.providers.base import Provider, ProviderAccount


class SMSAccount(ProviderAccount):
    def to_str(self):
        return self.account.extra_data.get('phone_number', '')


class SMSProvider(Provider):
    id = 'sms'
    name = 'SMS'
    account_class = SMSAccount

    def get_login_url(self, request, **kwargs):
        return "sms_auth_login"

    def extract_uid(self, data):
        return str(data['phone_number'])

    def extract_common_fields(self, data):
        return dict(
            phone_number=data.get('phone_number'),
        )

    def extract_extra_data(self, data):
        return dict(
            phone_number=data.get('phone_number'),
        )


from allauth.socialaccount.providers.base import Provider, ProviderAccount


class SMSAccount(ProviderAccount):
    def to_str(self):
        return self.account.extra_data.get('phone_number', '')


class SMSProvider(Provider):
    id = 'sms'
    name = 'SMS'
    account_class = SMSAccount

    def get_login_url(self, request, **kwargs):
        from django.urls import reverse
        return reverse('sms_login')

    def extract_uid(self, data):
        return str(data['phone_number'])

    def extract_common_fields(self, data):
        return dict(
            phone_number=data.get('phone_number'),
        )

    def extract_extra_data(self, data):
        return dict(
            phone_number=data.get('phone_number'),
        )


provider_classes = [SMSProvider]
