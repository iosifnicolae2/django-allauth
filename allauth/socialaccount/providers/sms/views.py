from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from allauth.socialaccount import app_settings
from allauth.account.internal.decorators import login_not_required
from allauth.socialaccount.helpers import (
    complete_social_login,
)
from allauth.socialaccount.models import SocialLogin
from allauth.utils import get_form_class

from .forms import SMSVerifyForm, SMSLoginForm
from .provider import SMSProvider


@login_not_required
class SMSLoginView(View):
    template_name = "sms/login.html"
    form_class = SMSLoginForm
    provider_class = SMSProvider

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "sms_login", self.form_class)

    def dispatch(self, request, *args, **kwargs):
        app = app_settings.PROVIDERS.get(SMSProvider.id)
        self.provider = self.provider_class(request, app)
        self.sms_verification_handler = self.provider.get_sms_verification_handler()
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.get_form()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.get_form()
        if form.is_valid():
            try:
                return self.perform_sms_verification(form)
            except Exception as e:
                form._errors["phone_number"] = form.error_class([str(e)])
                if settings.DEBUG:
                    raise e

        return render(request, self.template_name, {"form": form})

    def get_form(self):
        if self.request.method == "GET":
            return self.form_class(
                initial={
                    "next": self.request.GET.get(REDIRECT_FIELD_NAME),
                    "process": self.request.GET.get("process"),
                }
            )

        return self.form_class(self.request.POST)

    def get_callback_url(self):
        return reverse(verify)

    def perform_sms_verification(self, form):
        request = self.request
        phone_number = form.cleaned_data["phone_number"]

        sms_verification = self.sms_verification_handler.create_verification(request, phone_number)

        SocialLogin.stash_state(request)

        # Store data for verification
        request.session['sms_verification_id'] = sms_verification.pk
        if form.cleaned_data.get("next"):
            request.session['sms_next'] = form.cleaned_data["next"]

        return HttpResponseRedirect(self.get_callback_url())


@method_decorator(login_not_required, name="dispatch")
class SMSVerifyView(View):
    template_name = "sms/verify.html"
    form_class = SMSVerifyForm
    provider_class = SMSProvider

    def get_form_class(self):
        return get_form_class(app_settings.FORMS, "sms_verify", self.form_class)

    def dispatch(self, request, *args, **kwargs):
        app = app_settings.PROVIDERS.get(SMSProvider.id)
        self.provider = self.provider_class(request, app)
        self.sms_verification_handler = self.provider.get_sms_verification_handler()
        if 'sms_verification_id' not in request.session:
            return HttpResponseRedirect(reverse('sms_login'))
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            try:
                return self.complete_verification(form)
            except Exception as e:
                form._errors["code"] = form.error_class([str(e)])
                if settings.DEBUG:
                    raise e

        return render(request, self.template_name, {"form": form})

    def complete_verification(self, form):
        request = self.request
        verification_id = request.session['sms_verification_id']
        code = form.cleaned_data['code']

        verification = self.sms_verification_handler.verify_code(request, verification_id, code)

        if not verification:
            raise Exception("Invalid or expired verification code")

        # Clear verification data
        del request.session['sms_verification_id']

        # Complete login
        login = self.provider.sociallogin_from_response(
            request,
            {'phone_number': verification.phone_number.as_e164}
        )
        login.state = SocialLogin.unstash_state(request)

        # Handle next URL if present
        if 'sms_next' in request.session:
            login.state['next'] = request.session.pop('sms_next')

        return complete_social_login(request, login)


login = SMSLoginView.as_view()
verify = csrf_exempt(SMSVerifyView.as_view())
