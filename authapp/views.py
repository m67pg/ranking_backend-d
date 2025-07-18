from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework.decorators import api_view
from django.middleware.csrf import get_token

@csrf_exempt
@ensure_csrf_cookie
def login_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            token = get_token(request)
            return JsonResponse({'message': 'ログイン成功', 'username': user.username, 'csrfToken': token}, status=200)
        else:
            return JsonResponse({'error': '無効なユーザー名またはパスワードです。'}, status=401)

@csrf_exempt
def logout_user(request):
    logout(request)
    return JsonResponse({'message': 'ログアウトしました。'}, status=200)

@api_view(['GET'])
@ensure_csrf_cookie
def check_login_status(request):
    if request.user.is_authenticated:
        token = get_token(request)
        return JsonResponse({'isLoggedIn': True, 'username': request.user.username, 'csrfToken': token})
    else:
        return JsonResponse({'isLoggedIn': False})

