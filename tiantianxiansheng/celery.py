'''
celery的配置文件
'''
import os
from django.conf import settings
from celery import Celery

#为celery设置环境变量,告诉celery,jdaong的配置文件在哪
os.environ.setdefault('DJANGO_SETTINGS_MODULE','tiantianxiansheng.settings')


#创建应用
#创建celery类的实例对象
#Celery('name',broker='redis://你想用的redis服务端的ip地址/数据库号')
app = Celery('celery_tasks.tasks')


#配置应用
app.conf.update(
    #配置broker
    BROKER_URL ='redis://:123456@49.232.142.68:6379/1',
)

#设置celery的应用app自动去找工人(任务函数)
app.autodiscover_tasks(settings.INSTALLED_APPS)
