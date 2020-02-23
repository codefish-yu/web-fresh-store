from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from db.base_model import BaseModel
# Create your models here.
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


class User(AbstractUser,BaseModel):
    '''用户表'''

    #生成用户签名字符串
    def generate_active_token(self):
        serializer = Serializer(settings.SECRET_KEY,3600)
        info = {'confirm':self.id}
        token = serializer.dumps(info)
        return token.decode()

    class Meta:
        db_table = 'df_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name

class AddressManager(models.Manager):
    '''自定义地址模型管理器类'''
    #作用:
    #1. 改变原有查询的结果集:all()
    #2. 封装方法:让用户操作模型类对应的数据表(增删改查)

    #自定义获取用户默认收获地址的功能
    def get_default_address(self,user):
        try:
            #self.model:该属性获得实例化的对象所在的模型类(哪个模型类中实例化就是哪个模型类)
            default_addr = self.get(user=user,is_default=True)
        #当没有默认地址时,返回None
        except self.model.DoesNotExist:
            default_addr = None

        return default_addr


class Address(BaseModel):
    '''收件人地址类'''
    user = models.ForeignKey('User',verbose_name='所属账户')
    receiver = models.CharField(max_length=20,verbose_name='收件人')
    addr = models.CharField(max_length=256,verbose_name='收件地址')
    zip_code = models.CharField(max_length=6,null=True,verbose_name='邮政编码')
    phone = models.CharField(max_length=11,verbose_name='联系电话')
    is_default = models.BooleanField(default=False,verbose_name='是否默认')

    #实例化地址管理器模型类,这样就可以在Address中使用AddressManager中的方法了
    objects = AddressManager()



    class Meta:
        db_table = 'df_address'
        verbose_name = '地址'
        verbose_name_plural = verbose_name


