from django.http import JsonResponse
from user.models import UserProfile
import redis

def test_api(request):
    # return JsonResponse({'code':200})
    pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
    r=redis.Redis(connection_pool=pool)
    #分布式锁
    try:
        with r.lock('fangzhiyuan', blocking_timeout=3) as lock:
            u = UserProfile.objects.get(username='fangzhiyuan')
            u.score += 1
            u.save()
    except Exception as e:
        print('lock is failed is %s'%(e))

    return JsonResponse({'msg':'test is ok!'})