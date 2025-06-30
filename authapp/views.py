from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.views.decorators.csrf import ensure_csrf_cookie

@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'ログイン成功', 'username': user.username}, status=200)
        else:
            return JsonResponse({'error': '無効なユーザー名またはパスワードです。'}, status=401)

@csrf_exempt
def logout_user(request):
    logout(request)
    return JsonResponse({'message': 'ログアウトしました。'}, status=200)

@ensure_csrf_cookie
def check_login_status(request):
    if request.user.is_authenticated:
        return JsonResponse({'isLoggedIn': True, 'username': request.user.username})
    else:
        return JsonResponse({'isLoggedIn': False})
