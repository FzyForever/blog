import time
import jwt
from django.shortcuts import render
from django.http import JsonResponse
from . import models
import json
import hashlib
from btoken.views import make_token
from tools.loging_decorator import loging_check

# Create your views here.
@loging_check('PUT')
def users(request,username=None):
    if request.method=='GET':
        if username:
            try:
                user=models.UserProfile.objects.get(username=username)
            except models.UserProfile.DoesNotExist:
                user=None
            if not user:
                result={'code':208,'error':'The user not exist'}
                return JsonResponse(result)
            if request.GET.keys():
                data={}
                for k in request.GET.keys():
                    if hasattr(user,k):
                        data[k]=getattr(user,k)
                result={'code':200,'username':username,'data':data}
                return JsonResponse(result)
            else:
                data={'info':user.info,'sign':user.sign,'nickname':user.nickname, 'avatar':str(user.avatar),'email':user.email}
                result={'code':200,'username':username,'data':data}
                return JsonResponse(result)
        else:
            users=models.UserProfile.objects.all()
            res=[]
            for u in users:
                data={}
                data['username']=u.username
                data['email']=u.email
                res.append(data)
            result={'code':200,'data':res}
            return JsonResponse(result)

    elif request.method=='POST':
        json_str=request.body
        if not json_str:
            result={'code':202,'error':'Please Post Data'}
            return JsonResponse(result)
        json_obj=json.loads(json_str)
        username=json_obj.get("username")
        email=json_obj.get("email")
        password_1=json_obj.get("password_1")
        password_2=json_obj.get("password_2")
        if not username:
            result={'code':203,'error':'Please give me username'}
            return JsonResponse(result)
        if not email:
            result={'code':204,'error':'Please give me email'}
            return JsonResponse(result)
        if not password_1 or not password_2:
            result={'code':205,'error':'Please give me Password'}
            return JsonResponse(result)
        if password_1!=password_2:
            result={'code':206,'error':'Password not equal'}
            return JsonResponse(result)

        old_user=models.UserProfile.objects.filter(username=username)
        if old_user:
            result={'code':207,'error':'The username is existed!!!'}
            return JsonResponse(result)
        h_p=hashlib.sha1()
        h_p.update(password_1.encode())
        try:
            models.UserProfile.objects.create(username=username,nickname=username,email=email,password=h_p.hexdigest())
        except Exception as e:
            print("UserProfile create error is %s"%(e))
            result={'code':207,'error':'The username is existed!!!'}
            return JsonResponse(result)

        token=make_token(username)
        result={'code':200,'username':username,'data':{'token':token.decode()}}
        return JsonResponse(result)


    elif request.method=='PUT':
        # users=models.UserProfile.objects.filter(username=username)
        # if not users:
        #     result={'code':208,'error':'The user is not exist'}
        #     return JsonResponse(result)
        user=request.user
        json_str=request.body
        if not json_str:
            result={'code':202,'error':'Please Put Data'}
            return JsonResponse(result)

        json_obj=json.loads(json_str)

        nickname=json_obj.get("nickname")
        if not nickname:
            result={'code':209,'error':"The nickname is none！"}
            return JsonResponse(result)

        sign=json_obj.get('sign','')
        info=json_obj.get('info','')

        # 存
        user.sign=sign
        user.info=info
        user.nickname=nickname
        user.save()
        result={'code':200,'username':username}
        return JsonResponse(result)
#     #
#     # return JsonResponse({'code': 200, 'data': {'username': 1}})

@loging_check("POST")
def user_avatar(request,username):
    if not request.method=='POST':
        result={'code':210,'error':'Please Use Post'}
        return JsonResponse(result)

    users=models.UserProfile.objects.filter(username=username)
    if not users:
        result={'code':208,'error':'The user is not exist'}
        return JsonResponse(result)

    if request.FILES.get("avatar"):
        users[0].avatar=request.FILES.get('avatar')
        users[0].save()
        result={'code':200,'username':username}
        return JsonResponse(result)
    else:
        result={'code':211,'error':'Please give me avatar'}
        return JsonResponse(result)


