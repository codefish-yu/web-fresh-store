import re

from django.core import mail
from django.core.urlresolvers import reverse    #url反向解析
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import View

from apps.goods.models import GoodsSKU   #这里尽然不用加apps.goods.models
from tiantianxiansheng import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer  #加密用
from itsdangerous import SignatureExpired   #用于过期时异常处理
from celery_tasks.tasks import send_register_active_email
from .models import User, Address
from django.contrib.auth import authenticate, login, logout  # django内置的用户系统的用户登录认证等
from utils.mixin import LoginRequiredMixin
from django_redis import get_redis_connection

# Create your views here.


#/user/register
#类视图
class RegisterView(View):
    #显示注册页面
    def get(self,request):
        return render(request,'register.html')

    #注册
    def post(self,request):
        # 接收数据
        username = request.POST.get('user_name')  # user_name为前端该标签的name
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        # 用户协议
        allow = request.POST.get('allow')

        # 数据校验
        # 1. 判断用户是否都填了,不完整重新返回注册页面并提示：数据不完整
        if not all([username, password, email]):
            return render(request, 'register.html', {'errmsg': '数据不完整'})
        # 2. 校验传来的邮箱格式是否正确
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        # 3. 校验用户是否勾选同意协议,当用户勾选checkbox时，前端传过来的是：on
        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})
        # 4. 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        # 如果用户名不存在，说明该用户名可用
        except User.DoesNotExist:
            user = None
        # 如果用户名已存在
        if user:
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # 业务处理：进行用户注册
        # django提供的用户认证系统创建用户需要用：create_user()
        user = User.objects.create_user(username, email, password)
        # 将刚创建的用户都置于不激活
        user.is_active = 0
        user.save()

        #发送用户激活的邮件，包含激活链接(激活链接还总需要包含用户的省份信息):http://127.0.0.1:8000/user/active/用户mysql_id
        #用户mysql_id需要加密(身份信息)
        #1. 使用itsdangerous模块加密用户的身份信息，生成激活token
        serializer = Serializer(settings.SECRET_KEY,3600)   #将settings.py中的secret_key引进来当作现成的密钥，3600为国企时间
        info = {'confirm':user.id}
        token = serializer.dumps(info).decode()  #加密返回的是bytes，需要decode()

        #发邮件,
        #经过app.task装饰之后就有了delay()方法
        #使用delay()就可以将任务放入任务队列
        send_register_active_email.delay(email,username,token)

        # 注册完跳转到首页
        return redirect(reverse('goods:index'))  # 反向解析:reverse('主路由中name:分路由中name')

#激活用户
class ActiveView(View):
    #激活用户
    def get(self,request,token):    #token这个参数从re捕获的Url中传来，是用户的mysql数据表id
        #解密，获取用户信息info,并激活该用户,激活后跳转到登录页面
        serializer = Serializer(settings.SECRET_KEY,3600)
        try:
            info = serializer.loads(token)
            user_id = info['confirm']

            #激活
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()

            #跳转到登录页面,使用url反向解析
            return redirect(reverse('user:login'))

        #用于处理激活链接已过期的情况
        except SignatureExpired as e:
            return HttpResponse('激活链接已过期')

#登录
#url:http://127.0.0.1:8000/user/login
class LoginView(View):
    #显示登录页面
    def get(self,request):
        #判断是否勾选记住用户名
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''

        return render(request,'login.html',{'username':username,'checked':checked})

    #登录
    def post(self,request):
        '''登录校验'''
        #接收数据
        username = request.POST.get('username')
        password = request.POST.get('pwd')


        #校验数据
        #校验用户是否都输了
        if not all([username,password]):
            return render(request,'login.html',{'errmsg':'数据不完整'})


        #业务处理：登录校验
        #使用django内置的用户认证系统时，有一个函数authenticate(),可以校验用户名和密码
        #帮我们省略了password解码的步骤
        user = authenticate(username=username,password=password)
        if user is not None:
            #如果用户已激活，记录下用户的会话状态,并跳转到首页
            if user.is_active:
                #django内置的用户认证系统的login()已经封装了session
                login(request,user) #login(reqeust,user)将user.id保存到session中

                #获取登录后要跳转到的地址，默认跳转到首页
                #用login_required()装饰器之后，目标地址会跟在查询字符串中：?next=xxx,可以使用get('next')取出
                #前端登录表单中没有设置action,当没有设置action时，表单数据会提交到浏览器地址栏中的地址
                next_url = request.GET.get('next',reverse('goods:index'))   #reverse('goods:index')为默认值

                #跳转到登录后的目标地址，并判断用户是否勾选记住用户名
                response = redirect(next_url)#redirect返回的是httpResponseRedirect类的对象
                remember = request.POST.get('remember')
                #勾选则记住cookies:set_cookie('cookie名',cookie值,过期时间=xxx)
                if remember == 'on':
                    response.set_cookie('username',username,max_age=7*24*3600)
                #否则删除cookies
                else:
                    response.delete_cookie('username')

                #跳转
                return response


            else:
                return render(request,'login.html',{'errmsg':'帐号未激活'})
        else:
            return render(request,'login.html',{'errmsg':'用户名或密码错误'})

#url:http://127.0.0.1:8000/user/logout
class LogoutView(View):
    # 退出登录,也使用django的用户认证系统
    def get(self,request):
        #清除用户的session信息,logout()为django认证系统函数
        logout(request)

        #跳转到首页
        return redirect(reverse('goods:index'))


#用户中心信息页面:http://127.0.0.1.:8000/user
#需要先判断是否已经登录，在url中套用装饰器：login_required()
class UserInfoView(LoginRequiredMixin,View):
    #显示用户中心信息页面
    def get(self,request):
        #请求过来后，模板层会先根据用户登录状态显示不同的网页欢迎信息，详见模板层

        #获取用户的个人信息
        user = request.user
        default_addr = Address.objects.get_default_address(user)
        # default_addr = {user:xxx,phone:xxx,addr:xxx.....}

        #获取用户的历史浏览记录
        #用户历史浏览记录存在redis数据库中(缓存),流程是在用户访问商品详情页时存,在访问个人信息页时取(显示)
        con = get_redis_connection('default')

        #用户id,从redis中取出的数据格式为:history_用户id:[1,2,3]
        #拼接历史浏览记录的key
        history_key = 'history_%d' %user.id

        #获取用户最新浏览的5条商品id
        #lrange是Python操作redis的list的方法
        sku_ids = con.lrange(history_key,0,4)

        #遍历用户浏览的商品id,从商品表:GoodSKU中查询用户浏览的商品的具体信息
        #数据库返回给你的数据顺序是按照他存的顺序给你返回,和用户访问页面的顺序不一样
        goods_li = []
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=id)
            goods_li.append(goods)

        #组织传给模板的数据
        context = {'page':'user',
                   'address':default_addr,
                   'goods_li':goods_li}

        #给模板中传个标记：page='user',代表拿的是信息页面，然后在页面中做点渲染
        #将数据库中的默认收件地址信息传入模板
        return render(request,'user_center_info.html',context)


# 用户中心信息页面:http://127.0.0.1:8000/user/order
#需要先判断是否已经登录，在url中套用装饰器：login_required()
class UserOrderView(LoginRequiredMixin,View):   #多继承，使用到了LoginRequired类的as_view()
    # 显示用户中心订单页面
    def get(self, request):
        # 给模板中传个标记：page='order',代表拿的是信息页面，然后在页面中做点渲染
        return render(request, 'user_center_order.html',{'page':'order'})


# 用户中心信息页面:http://127.0.0.1:8000/user/address
#需要先判断是否已经登录，在url中套用装饰器：login_required()
class AddressView(LoginRequiredMixin,View):
    # 显示用户中心地址页面
    def get(self, request):
        #获取登录的用户对象
        user = request.user
        #获取用户的默认收获地址
        #这里使用自定义模型管理器类中的方法
        default_addr = Address.objects.get_default_address(user)

        # 给模板中传个标记：page='address',代表拿的是信息页面,然后在页面中做点渲染
        #将default_addr传过去,用于判断显示地址
        return render(request, 'user_center_site.html',{'page':'address','address':default_addr})

    #添加地址
    def post(self,request):
        #接收前端传来的表单数据:receiver,zip_code,addr,phone
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        #校验数据
        if not all([receiver,addr,phone]):  #不校验邮编,因为现在基本不用邮编了
            return render(request,'user_center_site.html',{'errmsg':'数据不完整'})

        #校验手机号
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$',phone):
            return render(request,'user_center_site.html',{'errmsg':'手机格式不正确'})

        #业务处理:添加地址
        #如果用户已存在默认收获地址,添加的地址不作为默认收获地址,否则作为默认收获地址
        #获取登录用户,这里user是Address表的外键,关联User表
        user = request.user
        #判断该用户是否有默认地址
        #这里使用自定义模型管理器类中的方法(在models层自定义了一个模型管理器类,就是对objects进行了重写,让他有了新的方法)
        default_addr = Address.objects.get_default_address(user)

        #Address表中字段:user,receiver,addr,zip_code,phone,is_default
        if default_addr:
            is_default = False
        else:
            is_default = True
        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default)

        #返回应答,刷新地址页面,redirect()是get方式,触发上面的get(request)
        return redirect(reverse('user:address'))
















