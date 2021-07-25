from django.urls import re_path
from cryptocurrency.auth.views import SignInView, SignUpView, ValidateSession

urlpatterns = [
    re_path(r'signin/?$', SignInView.as_view()),
    re_path(r'signup/?$', SignUpView.as_view()),
    re_path(r'validateSession/?$', ValidateSession.as_view()),
]
