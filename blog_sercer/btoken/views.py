from django.shortcuts import render
from django.http import JsonResponse
import json
from user.models import UserProfile
import hashlib
import time
import jwt


# Create your views here.
def btoken(request):
    if not request.method=='POST':
        result={'code':101,'error':'Please Use Post'}
        return JsonResponse(result)

    json_str=request.body
    if not json_str:
        result={'code':102,'error':'Please Post Data'}
        return JsonResponse(result)

    json_obj=json.loads(json_str)
    username=json_obj.get("username")
    password=json_obj.get("password")

    if not username:
        result={'code':103,'error':'Please Give me username'}
        return JsonResponse(result)
    if not password:
        result={'code':104,'error':'Please Give me password'}
        return JsonResponse(result)

    Users=UserProfile.objects.filter(username=username)

    if not Users:
        result={'code':105,'error':'The username is not exist'}
        return JsonResponse(result)

    p_m=hashlib.sha1()
    p_m.update(password.encode())
    if p_m.hexdigest() != Users[0].password:
        result={'code':106,'error':'The username or password is not right'}
        return JsonResponse(result)

    token=make_token(username)
    result={'code':200,'username':username,'data':{'token':token.decode()}}
    return JsonResponse(result)

def make_token(username,expire=3600*24):
    key='abcdef1234'
    now_t=time.time()
    payload={'username':username,'exp':int(now_t+expire)}
    return jwt.encode(payload,key,algorithm='HS256')