from django.conf.urls import url
from .views import IndexView

from . import views

urlpatterns = [
    #首页：http://127.0.0.1:8000
    url(r'^$',IndexView.as_view(),name='index'),
]