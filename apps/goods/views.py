from django.shortcuts import render
from django_redis import get_redis_connection

from .models import GoodsType, IndexGoodsBanner, IndexTypeGoodsBanner

# Create your views here.

#首页:http://127.0.0.:8000
from django.views import View


class IndexView(View):
    def get(self,request):
        '''显示首页'''
        #获取商品的种类信息:新鲜水果,海鲜水产等
        types = GoodsType.objects.all()

        #获取首页轮播商品信息:商品轮播表
        goods_banners = IndexGoodsBanner.objects.all().order_by('index')

        #获取首页促销活动信息:商品促销表
        promotion_banners = IndexTypeGoodsBanner.objects.all().order_by('index')

        #获取首页分类商品展示信息:各分类下商品的具体信息
        for type in types:
            #获取所有以图片展示的type种类的首页分类商品展示信息
            image_banners = IndexTypeGoodsBanner.objects.filter(type=type,display_type=1)
            #获取所有以文字展示的type种类的首页分类商品的展示信息
            title_banners = IndexTypeGoodsBanner.objects.filter(type=type,display_type=0)

            #动态给type增加属性,分别保存以图片展示和以文字展示的首页分类商品的信息
            #type是GoodsType类的实例,通过在类的外面给实例添加属性的方式给该种类的商品添加信息
            type.image_banners = image_banners
            type.title_banners = title_banners

        #获取用户购物车中商品的数目
        user = request.user
        cart_count = 0
        #使用django用户认证系统的is_authenticated()判断用户是否已登陆
        if user.is_authenticated():
            #购物车中信息是以散列形式存储在redis缓存中,连接redis
            conn = get_redis_connection('default')
            #拼该用户的购物车的key
            cart_key = 'cart_%d'%user.id
            #hlen返回该key的值的个数
            cart_count = conn.hlen(cart_key)

        #组织传给模板的信息
        context = {'type':types,
                   'goods_banners':goods_banners,
                   'promotion_banners':promotion_banners,
                   'cart_count':cart_count}

        #渲染模板
        return render(request,'index1.html',context)


