from django.urls import re_path
from django.views.decorators.csrf import csrf_exempt
from cryptocurrency.blockchain.views import ChainView, ChainUserView

urlpatterns = [
    re_path(r'check/?$', csrf_exempt(ChainView.as_view())),
    re_path(r'chain_user/?$', ChainUserView.as_view()),
]
