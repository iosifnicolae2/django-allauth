from django.conf import settings
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.views import View
import random
from sms import Message

from allauth.socialaccount.adapter import get_adapter


class SMSAuthenticationView(View):
    def post(self, request):
        phone_number = request.POST.get('phone_number')
        if not phone_number:
            return JsonResponse({'error': 'Phone number is required'}, status=400)

        # Generate verification code
        code = str(random.randint(100000, 999999))

        # Store the code securely
        request.session['sms_verification_code'] = code
        request.session['sms_phone_number'] = phone_number

        # Send SMS
        context = {
            "code": code
        }

        to_phone_number = [phone_number] if isinstance(phone_number, str) else phone_number
        content = render_to_string("sms/sms_content.txt", context)

        success = Message(
            content,
            settings.SMS_FROM_NUMBER,
            to_phone_number
        ).send()

        if not success:
            return JsonResponse({'error': 'Failed to send SMS'}, status=500)

        return JsonResponse({'message': 'Verification code sent'})

login = SMSAuthenticationView.as_view()

class SMSVerifyView(View):
    def post(self, request):
        code = request.POST.get('code')
        stored_code = request.session.get('sms_verification_code')
        phone_number = request.session.get('sms_phone_number')

        if not all([code, stored_code, phone_number]):
            return JsonResponse({'error': 'Invalid request'}, status=400)

        if code != stored_code:
            return JsonResponse({'error': 'Invalid verification code'}, status=400)

        # Clear session data
        del request.session['sms_verification_code']
        del request.session['sms_phone_number']

        # Create social login
        provider = get_adapter().get_provider(request, 'sms')

        # Create response data
        response = {
            'phone_number': phone_number,
        }

        social_login = provider.sociallogin_from_response(request, response)

        # Complete login
        social_login.save(request)
        return JsonResponse({'success': True})

verify = SMSVerifyView.as_view()
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib import messages

from allauth.account.internal.decorators import login_not_required
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.models import SocialLogin

from ..base import AuthError
from .forms import SMSLoginForm, SMSVerifyForm
from .provider import SMSProvider
from .utils import SMSVerificationStore


@method_decorator(login_not_required, name="dispatch")
class SMSLoginView(View):
    template_name = "sms/login.html"
    form_class = SMSLoginForm
    provider_class = SMSProvider

    def dispatch(self, request, *args, **kwargs):
        self.provider = self.provider_class(request)
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
        provider = self.provider
        phone_number = form.cleaned_data["phone_number"]
        
        store = SMSVerificationStore()
        verification = store.create_verification(phone_number)
        
        if not verification.send():
            raise Exception("Failed to send verification code")

        SocialLogin.stash_state(request)
        
        # Store data for verification
        request.session['sms_verification_id'] = verification.id
        if form.cleaned_data.get("next"):
            request.session['sms_next'] = form.cleaned_data["next"]
            
        return HttpResponseRedirect(self.get_callback_url())


@method_decorator(login_not_required, name="dispatch")
class SMSVerifyView(View):
    template_name = "sms/verify.html"
    form_class = SMSVerifyForm
    provider_class = SMSProvider

    def dispatch(self, request, *args, **kwargs):
        self.provider = self.provider_class(request)
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

        return render(request, self.template_name, {"form": form})

    def complete_verification(self, form):
        request = self.request
        verification_id = request.session['sms_verification_id']
        code = form.cleaned_data['code']
        
        store = SMSVerificationStore()
        verification = store.get_verification(verification_id)
        
        if not verification or not verification.verify(code):
            raise Exception("Invalid or expired verification code")
            
        # Clear verification data
        del request.session['sms_verification_id']
        store.remove_verification(verification_id)
        
        # Complete login
        login = self.provider.sociallogin_from_response(
            request, 
            {'phone_number': verification.phone_number}
        )
        login.state = SocialLogin.unstash_state(request)
        
        # Handle next URL if present
        if 'sms_next' in request.session:
            login.state['next'] = request.session.pop('sms_next')
            
        return complete_social_login(request, login)


login = SMSLoginView.as_view()
verify = csrf_exempt(SMSVerifyView.as_view())
