import json
from django.http import JsonResponse

def submission(request):
  try:
    return json.loads(request.body.decode(encoding='UTF-8'))
  except:
    if request.method in ("PUT", "POST"):
      return request.POST
    else:
      return request.GET
    
def rest_api_decorator(view_func):
  def wrapper(view, *args, **kwargs):
    from django.contrib.auth.models import User
    request = args[0]
    token = request.headers.get("cookie", "token=")[6:]
    user = User.objects.filter(auth_token=token)
    if not user.count():
      return JsonResponse({
        "status": "error",
        "message": "Invalid cookies"
      }, headers = {
        "Set-Cookie": "token=; Path=/; Secure; HttpOnly; expires=Thu, 01 Jan 1970 00:00:00 GMT"
      },
      status=403)
    view.user = user
    return view_func(view, *args, **kwargs)
  return wrapper