'''定义搜索引擎的索引类'''
from haystack import indexes
#导入你的模型类
from apps.goods.models import GoodsSKU

#定义对于GoodsSKU模型类的索引类
#索引类名格式：模型类名＋Index
class GoodsSKUIndex(indexes.SearchIndex,indexes.Indexable):
    #use_template指定根据表中的哪些字段建立索引文件的说明放在一个文件中
    text = indexes.CharField(document=True,use_template=True)

    def get_model(self):
        #返回你的模型类
        return GoodsSKU

    #建立索引的数据
    def index_queryset(self,using=None):
        return self.get_model().objects.all()
