from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from .views import RegisterView, ActiveView, LoginView, UserInfoView, UserOrderView, AddressView, LogoutView

urlpatterns = [
    #http://127.0.0.1:8000/user/register
    #使用类视图的方式注册，as_view()是从view类中继承来的方法
    url(r'^register$',RegisterView.as_view(),name='register'),
    #该url就是用户激活的链接,需要用re将该用户在Mysql中user_id捕获给后端
         #http://127.0.0.1:8000/user/active/user_id
    url(r'^active/(?P<token>.*)$',ActiveView.as_view(),name='active'),
    #登录：http://127.0.0.1:8000/user/login
    url(r'^login$',LoginView.as_view(),name='login'),
    #退出：http://127.0.0.1:8000/user/logout
    url(r'^logout$',LogoutView.as_view(),name='logout'),
    #用户中心－用户信息页:http://127.0.0.1:8000/user
    url(r'^$',UserInfoView.as_view(),name='user'),  #UserInfoView.as_view():类.类方法
    #用户中心－订单页http://127.0.0.1:8000/user/order
    url(r'^order',UserOrderView.as_view(),name='order'),
    #用户中心－地址页,http://127.0.0.1:8000/user/address
    url(r'^address',AddressView.as_view(),name='address'),

]