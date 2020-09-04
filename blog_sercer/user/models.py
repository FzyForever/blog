from django.db import models

# Create your models here.
class UserProfile(models.Model):
    username=models.CharField(verbose_name="用户名",max_length=11,primary_key=True)
    nickname=models.CharField(verbose_name="昵称",max_length=30)
    email=models.CharField(verbose_name="邮箱",max_length=50)
    password = models.CharField(max_length=40,verbose_name='密码')
    sign = models.CharField(max_length=50, verbose_name='个人签名')
    info = models.CharField(max_length=150, verbose_name='个人描述')
    avatar=models.ImageField(upload_to='avatar/')
    score=models.IntegerField(verbose_name=u'分数',null=True,default=0)

    class Meta:
        db_table='user_profile'
