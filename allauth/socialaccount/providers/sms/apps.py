from django.apps import AppConfig

class SMSProvider(AppConfig):
    name = 'allauth.socialaccount.providers.sms'
    verbose_name = 'SMS Authentication Provider'
