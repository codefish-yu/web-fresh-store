from django.contrib.auth.decorators import login_required


#工具类视图
#用于当项目中用到装饰器login_required()非常多时,不用在url中一个个套login_required()
#直接在这个工具类中使用login_required()装饰下as_view()
#然后在url层引入该新写的修改了性能的as_view()
class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        #调用父类的as_view,返回一个值
        #super(LoginRequiredMixin,cls)表示调用LoginRequiredMixin类的父类
        view = super(LoginRequiredMixin,cls).as_view(**initkwargs)
        return login_required(view)