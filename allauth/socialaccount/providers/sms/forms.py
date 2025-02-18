from django import forms
from django.utils.translation import gettext_lazy as _

class SMSLoginForm(forms.Form):
    phone_number = forms.CharField(
        label=_("Phone Number"),
        help_text=_("Enter your phone number including country code (e.g. +1234567890)"),
    )
    next = forms.CharField(widget=forms.HiddenInput, required=False)
    process = forms.CharField(widget=forms.HiddenInput, required=False)

class SMSVerifyForm(forms.Form):
    code = forms.CharField(
        label=_("Verification Code"),
        help_text=_("Enter the verification code sent to your phone"),
        max_length=6,
        min_length=6,
    )
