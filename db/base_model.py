from django.db import models


class BaseModel(models.Model):
    '''模型类抽象基类'''
    create_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    update_time = models.DateTimeField(auto_now_add=True,verbose_name='更新时间')
    is_delete = models.BooleanField(default=False,verbose_name='删除标记')

    class Meta:
        #必须指明是抽象模型类,否则迁移时会报错
        abstract = True