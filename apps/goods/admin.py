from django.contrib import admin
from .models import GoodsType

# Register your models here.

#将该模型类GoodType注册到admin中
admin.site.register(GoodsType)


