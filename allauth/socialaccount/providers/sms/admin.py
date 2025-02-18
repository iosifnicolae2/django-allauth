from django.contrib import admin

from .models import SMSVerification


class SMSVerificationAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'created_at', 'verified')
    search_fields = ('phone_number',)
    list_filter = ('verified', 'created_at')


admin.site.register(SMSVerification, SMSVerificationAdmin)
