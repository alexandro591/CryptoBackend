from django.urls import re_path
from cryptocurrency.blockchain.views import ChainView, ChainUserView

urlpatterns = [
    re_path(r'check/?$', ChainView.as_view()),
    re_path(r'chain_user/?$', ChainUserView.as_view()),
]
