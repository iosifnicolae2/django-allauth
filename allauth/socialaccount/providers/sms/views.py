import random
from django.http import JsonResponse
from django.views import View
from django.core.exceptions import ValidationError

from allauth.socialaccount.adapter import get_adapter
from allauth.socialaccount.providers.base import AuthProcess
from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.providers.oauth2.views import OAuth2LoginView
from allauth.socialaccount.helpers import complete_social_login

class SMSAuthenticationView(View):
    def post(self, request):
        phone_number = request.POST.get('phone_number')
        if not phone_number:
            return JsonResponse({'error': 'Phone number is required'}, status=400)
        
        # Generate verification code
        code = str(random.randint(100000, 999999))
        
        # Store the code securely (you'll need to implement this)
        request.session['sms_verification_code'] = code
        request.session['sms_phone_number'] = phone_number
        
        # Send SMS (you'll need to implement this)
        self._send_sms(phone_number, code)
        
        return JsonResponse({'message': 'Verification code sent'})
    
    def _send_sms(self, phone_number, code):
        # Implement SMS sending logic here
        # You'll need to integrate with an SMS service provider
        pass

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
        social_login = self._create_social_login(request, provider, phone_number)
        
        # Complete login
        ret = complete_social_login(request, social_login)
        return JsonResponse({'success': True})
    
    def _create_social_login(self, request, provider, phone_number):
        # Create response data
        response = {
            'phone_number': phone_number,
        }
        
        social_login = provider.sociallogin_from_response(request, response)
        return social_login
