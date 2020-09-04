from django.shortcuts import render
from django.http import JsonResponse
from tools.loging_decorator import loging_check,get_user_by_request
import json
import datetime
from topic.models import Topic
from user.models import UserProfile
from message.models import Message


# Create your views here.
@loging_check('POST','DELETE')
def topics(request,author_id=None):
    if request.method=='POST':
        author=request.user

        json_str=request.body
        if not json_str:
            result={'code':302,'error':'Please give json'}
            return JsonResponse(result)
        json_obj=json.loads(json_str)
        title=json_obj.get("title")
        content=json_obj.get("content")
        content_text=json_obj.get("content_text")
        introduce=content_text[:30]
        limit=json_obj.get("limit")
        if limit not in ['public','private']:
            result={'code':303,'error':'Please give me right limit'}
            return JsonResponse(result)
        category=json_obj.get("category")
        if category not in ['tec','no-tec']:
            result={'code':304,'error':"Please give me right category"}
            return JsonResponse(result)

        now=datetime.datetime.now()

        #存储Topic
        Topic.objects.create(title=title,content=content,introduce=introduce,limit=limit,category=category,created_time=now,modified_time=now,
                             author=author)
        result={'code':200,'username':author.username}
        return JsonResponse(result)

    elif request.method=='DELETE':
        author=request.user
        if author.username!=author_id:
            result={'code':306,'error':'You can not do it'}
            return JsonResponse(result)

        topic_id=request.GET.get("topic_id")
        if not topic_id:
            result={'code':307,'error':'you can not do it!'}
            return JsonResponse(result)
        try:
            topic=Topic.objects.get(id=topic_id)
        except Exception as e:
            print("topic delete error is %s"%(e))
            result={'code':308,'error':'your topic is not existed'}
            return JsonResponse(result)
        topic.delete()
        return JsonResponse({'code':200})

    elif request.method=='GET':
        authors=UserProfile.objects.filter(username=author_id)
        if not authors:
            result={'code':305,'error':'The current author is not existed!'}
            return JsonResponse(result)
        author=authors[0]

        visitor=get_user_by_request(request)
        visitor_username=None
        if visitor:
            visitor_username=visitor.username

        t_id=request.GET.get("t_id")
        if t_id:
            t_id=int(t_id)
            is_self=None
            if visitor_username==author_id:
                is_self=True

                try:
                    author_topic=Topic.objects.get(id=t_id)
                except Exception as e:
                    result={'code':309,'error':'No topic'}
                    return JsonResponse(result)

            else:
                try:
                    author_topic=Topic.objects.get(id=t_id,limit='public')
                except Exception as e:
                    result={'code':309,'error':'No topic'}
                    return JsonResponse(result)

            #生成具体返回
            res=make_topic_res(author,author_topic,is_self)
            return JsonResponse(res)
        else:
            category=request.GET.get('category')

            if category in ['tec','no-tec']:
                if visitor_username==author_id:
                    author_topics=Topic.objects.filter(author_id=author_id,category=category)
                else:
                    author_topics=Topic.objects.filter(author_id=author_id,category=category,limit='public')
            else:
                if visitor_username==author_id:
                    author_topics=Topic.objects.filter(author_id=author_id)
                else:
                    author_topics=Topic.objects.filter(author_id=author_id,limit='public')


            res=make_topics_res(author,author_topics)
            return JsonResponse(res)

def make_topics_res(author,author_topics):
    res={'code':200,'data':{}}
    topics_res=[]
    for topic in author_topics:
        d={}
        d['id']=topic.id
        d['title']=topic.title
        d['category']=topic.category
        d['created_time']=topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
        d['introduce']=topic.introduce
        d['author']=topic.author.nickname
        topics_res.append(d)
    res['data']['topics']=topics_res
    res['data']['nickname']=author.nickname
    return res


def make_topic_res(author,author_topic,is_self):
    if is_self:
        next_topic=Topic.objects.filter(id__gt=author_topic.id,author=author).first()
        last_topic=Topic.objects.filter(id__lt=author_topic.id,author=author).last()

    else:
        next_topic=Topic.objects.filter(id_gt=author_topic.id,author=author,limit='public').first()
        last_topic=Topic.objects.filter(id_lt=author_topic.id,author=author,limit='public').first()

    if next_topic:
        next_id=next_topic.id
        next_title=next_topic.title

    else:
        next_id=None
        next_title=None

    if last_topic:
        last_id=last_topic.id
        last_title=last_topic.title
    else:
        last_id=None
        last_title=None

    #生成message返回结构
    all_messages = Message.objects.filter(topic=author_topic).order_by('-created_time')
    # leve1_msg = {1:[m1,m2,m3], 3,:[m4,m5,m6]}
    # messages = [ma_1, mb_3, mc_5 ]
    msg_list = []
    #key：是留言id, value是[回复对象,回复对象]
    level1_msg = {} # 'aaa': []
    #全部留言及回复的数量
    m_count = 0
    for msg in all_messages:
        m_count += 1
        if msg.parent_message:
            #回复
            level1_msg.setdefault(msg.parent_message, [])
            level1_msg[msg.parent_message].append({'msg_id':msg.id,'publisher':msg.publisher.nickname,'publisher_avatar':str(msg.publisher.avatar), 'content':msg.content,'created_time':msg.created_time.strftime('%Y-%m-%d')})
        else:
            #留言
            msg_list.append({'id':msg.id, 'content':msg.content,'publisher':msg.publisher.nickname,'publisher_avatar': str(msg.publisher.avatar), 'created_time':msg.created_time.strftime('%Y-%m-%d'), 'reply':[]})

    #关联，将 留言和回复进行合并
    for m in msg_list:
        if m['id'] in level1_msg:
            m['reply'] = level1_msg[m['id']]


    result = {'code': 200, 'data': {}}
    result['data']['nickname'] = author.nickname
    result['data']['title'] = author_topic.title
    result['data']['category'] = author_topic.category
    result['data']['created_time'] = author_topic.created_time.strftime('%Y-%m-%d')
    result['data']['content'] = author_topic.content
    result['data']['introduce'] = author_topic.introduce
    result['data']['author'] = author.nickname
    result['data']['next_id'] = next_id
    result['data']['next_title'] = next_title
    result['data']['last_id'] = last_id
    result['data']['last_title'] = last_title
    # 暂时为假数据
    result['data']['messages'] = msg_list
    result['data']['messages_count'] = m_count
    return result






