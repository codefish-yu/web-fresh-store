'''
自定义静态文件存储类,将django默认的文件存储行为(默认存储到MEDIA_ROOT指定的路径下)修改为存储到远程fastDFS中去
需要在django+nginx+fastdfs业务逻辑基础之上理解喜爱面的代码
'''
from django.core.files.storage import Storage   #重写文件存储类,必须继承自该类
from fdfs_client.client import Fdfs_client

from tiantianxiansheng import settings


class FDFSStorage(Storage):
    '''fastdfs文件存储类'''

    def __init__(self,client_conf=None,base_url=None):
        '''初始化'''
        #给用户自己传fastdfs客户端配置文件的选择,如果用户没传,就用我们的
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf

        #给用户自己传他的nginx路由的选择,如果用户没传,就用我们的
        if base_url is None:
            base_url = settings.FDFS_URL
        self.base_url = base_url


    #重写_open()方法,用于打开文件,规定必须重写,但是我们这里用不到,这届pass
    def _open(self,name,mode='rb'):
        pass

    def _save(self, name, content):
        '''
        :param name:你选择的上传文件的名字
        :param content:File类的对象，包含你上传的文件内容，有了这个对象就可以获取文件内容
        :return:
        '''
        # 创建一个fdfs_client对象
        client = Fdfs_client(self.client_conf)

        # 上传文件到fastdfs系统中
        # upload_by_buffer()方法是根据文件内容上传文件,回值格式为：
        #dict {
        #     'Group name'      : group_name,
        #     'Remote file_id'  : remote_file_id,
        #     'Status'          : 'Upload successed.',
        #     'Local file name' : '',
        #     'Uploaded size'   : upload_size,
        #     'Storage IP'      : storage_ip
        #     }
        res = client.upload_by_buffer(content.read())
        print(res)

        #判断是否上传成功
        if res.get('Status') != 'Upload successed.':
            #上传失败
            raise Exception('上传文件到fastdfs失败')

        #获取返回的文件id
        filename = res.get('Remote file_id')
        return filename

    # django在上传文件之前，会先调用该方法，用于判断文件名是否可用(但文件其实保存在fastdfs中，所以这里直接返回false就行)
    def exists(self,name):
        return False


    #该方法用于向nginx和fastdfs请求拿保存的静态文件
    #返回你要访问文件的url路径
    def url(self,name):
        '''
        :param name:django保存文件到fastdfs后fastdfs返回给django的文件id:groupxxxx...
        :return 你要访问的文件在nginx中的url
        '''
        return self.base_url + name
