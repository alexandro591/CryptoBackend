from cryptocurrency.utils.restapi import submission
from django.views import View
from django.http import JsonResponse
from rest_framework.authtoken.views import ObtainAuthToken
from cryptocurrency.utils.restapi import rest_api_decorator
from django.contrib.auth.models import User
from cryptocurrency.account.models import Account
from cryptocurrency.blockchain.models import Wallet


class SignInView(ObtainAuthToken):
  def post(self, request):
    response = super().post(request)
    token = response.data["token"]
    response.headers = {
      **response.headers,
      "Set-Cookie": f"token={token}; Path=/; Secure; HttpOnly"
    }
    return response

class SignUpView(View):
  def post(self, request):
    raw = submission(request)
    email = raw["email"]
    password = raw["password"] if raw["passwordConfirm"] == raw["password"] else None
    if not password:
      return JsonResponse({
          "status": "error",
          "message": "Passwords don't match"
        },
      status=400)
    user = User.objects.get(username=email, email=email, password=password)
    account = Account.objects.create(user=user)
    wallet = Wallet.objects.create(account=account)
    return JsonResponse({
      "account": wallet.to_dict
    })

class ValidateSession(View):
  @rest_api_decorator
  def get(self, request):
    return JsonResponse({
      "status": "success"
    })