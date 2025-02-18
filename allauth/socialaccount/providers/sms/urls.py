from django.urls import path
from . import views

urlpatterns = [
    path("sms/login/", views.login, name="sms_login"),
    path("sms/verify/", views.verify, name="sms_verify"),
]
from django.urls import path

from . import views


urlpatterns = [
    path("sms/login/", views.login, name="sms_login"),
    path("sms/verify/", views.verify, name="sms_verify"),
]
