from django import forms
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from phonenumber_field import widgets

from allauth.account.adapter import get_adapter
from allauth.core import context, ratelimit
from phonenumber_field.formfields import PhoneNumberField


class SMSLoginForm(forms.Form):
    phone_number = PhoneNumberField(
        label=_("Phone Number"),
        help_text=_("Enter your phone number with country code (e.g. +407XX XXX XXX)"),
        widget=widgets.RegionalPhoneNumberWidget(attrs={
            'placeholder': _('+407XX XXX XXX')
        })
    )
    next = forms.CharField(widget=forms.HiddenInput, required=False)
    process = forms.CharField(widget=forms.HiddenInput, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean_phone_number(self):
        adapter = get_adapter()
        phone_number = self.cleaned_data["phone_number"].as_e164

        if not ratelimit.consume(
            context.request,
            action="request_sms_login_code",
            key=phone_number
        ):
            raise adapter.validation_error("too_many_login_attempts")

        return phone_number

    @property
    def action_url(self):
        return reverse('sms_login')

    @property
    def submit_btn_label(self):
        return _("Sign in with SMS")

    @property
    def form_description(self):
        return _("Please type your phone number to receive a verification code.")

class SMSVerifyForm(forms.Form):
    code = forms.CharField(
        label=_("Verification Code"),
        help_text=_("Enter the code sent to your phone"),
        min_length=6,
        max_length=6,
    )
