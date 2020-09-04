from django.db import models
from topic.models import Topic
from user.models import UserProfile

# Create your models here.
class Message(models.Model):
    topic=models.ForeignKey(Topic)
    content=models.CharField(max_length=60,verbose_name='留言内容')
    publisher=models.ForeignKey(UserProfile)
    parent_message=models.IntegerField(verbose_name='回复的留言')
    created_time=models.DateTimeField()

    class Meta:
        db_table='message'