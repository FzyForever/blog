from django.http import JsonResponse
import jwt
from user.models import UserProfile

KEY="abcdef1234"

def loging_check(*method):
    def _loging_check(func):

        def wrapper(request,*args,**kwargs):

            token=request.META.get('HTTP_AUTHORIZATION')
            if not method:
                return func(request,*args,**kwargs)
            if not request.method in method:
                return func(request,*args,**kwargs)
            if not token or token =='null':
                result={'code':107,'error':'Please give me token'}
                return JsonResponse(result)
            try:
                res=jwt.decode(token,KEY,algorithms='HS256')
            except Exception as e:
                print("----token error is  %s"%(e))
                result={'code':108,'error':'Please Login'}
                return JsonResponse(result)

            username=res['username']
            user=UserProfile.objects.get(username=username)
            request.user=user
            return func(request,*args,**kwargs)

        return wrapper
    return _loging_check

def get_user_by_request(request):
    token=request.META.get("HTTP_AUTHORIZATION")
    if not token or token =='null':
        return None

    try:
        res=jwt.decode(token,KEY,algorithms='HS256')
    except Exception as e:
        print('---get_user_by_request-jwt decode error is %s'%(e))
        return None
    username=res['username']
    user=UserProfile.objects.get(username=username)
    return user


