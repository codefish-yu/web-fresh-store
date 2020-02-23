'''
    celery_tasks
'''
import time
from celery import Celery
from django.http import request
from django.shortcuts import render
from django_redis import get_redis_connection
# from goods.models import GoodsType, IndexGoodsBanner, IndexTypeGoodsBanner
from django.template import loader, RequestContext
from tiantianxiansheng.celery import app

from django.conf import settings
from django.core.mail import send_mail
from apps.goods.models import GoodsType, IndexGoodsBanner, IndexTypeGoodsBanner
import os
import django




#定义celery的任务函数(worker)
@app.task
def send_register_active_email(to_email,username,token):
    '''发送激活邮件'''
    #组织邮件信息
    subject = '天天生鲜欢迎信息'  # 标题
    # 邮件内容
    message = ''
    # 传html格式内容
    html_message = '<h1>%s,欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br/><a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>' % (
    username, token, token)
    # 发件人
    sender = settings.EMAIL_FROM
    # 收件人
    receiver = [to_email]
    send_mail(subject, message, sender, receiver, html_message=html_message)
    #测试使用celery处理第三方io不用等待５秒
    time.sleep(5)

@app.task
def generate_static_index_html():
    '''
    产生首页静态页面
    用户未登录状态下,首页的访问次数较多,但页面变化不大,使用celery将首页设置为静态页面
    '''
    # 获取商品的种类信息:新鲜水果,海鲜水产等
    types = GoodsType.objects.all()

    # 获取首页轮播商品信息:商品轮播表
    goods_banners = IndexGoodsBanner.objects.all().order_by('index')

    # 获取首页促销活动信息:商品促销表
    promotion_banners = IndexTypeGoodsBanner.objects.all().order_by('index')

    # 获取首页分类商品展示信息:各分类下商品的具体信息
    for type in types:
        # 获取所有以图片展示的type种类的首页分类商品展示信息
        image_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=1)
        # 获取所有以文字展示的type种类的首页分类商品的展示信息
        title_banners = IndexTypeGoodsBanner.objects.filter(type=type, display_type=0)

        # 动态给type增加属性,分别保存以图片展示和以文字展示的首页分类商品的信息
        # type是GoodsType类的实例,通过在类的外面给实例添加属性的方式给该种类的商品添加信息
        type.image_banners = image_banners
        type.title_banners = title_banners

    # 组织传给模板的信息
    context = {'type': types,
               'goods_banners': goods_banners,
               'promotion_banners': promotion_banners
               }

    #使用模板
    #1. 加载模板文件,使用django_templates模块
    temp = loader.get_template('static_index.html')
    #2. 渲染模板
    static_index_html = temp.render(context)

    #生成首页对应的静态文件
    #1. 设置生成文件的路径:是生成在celery任务这里的static文件夹下(腾讯云)
    save_path = os.path.join(settings.BASE_DIR,'static/index1.html')
    #2. 生成文件
    with open(save_path,'w') as f:
        f.write(static_index_html)

