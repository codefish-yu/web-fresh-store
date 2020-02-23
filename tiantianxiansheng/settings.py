"""
Django settings for tiantianxiansheng project.

Generated by 'django-admin startproject' using Django 1.11.8.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import sys


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '2zwc0jp-p8qg1g*2wjy01m4)mmk#%tc$p(pc$y0d8iqlg(t*#k'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tinymce',  #富文本编辑器
    'apps.user',
    'apps.goods',
    'apps.order',
    'apps.cart',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tiantianxiansheng.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        #定义templates的查找路径
        'DIRS': [os.path.join(BASE_DIR,'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'tiantianxiansheng.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

#指定django认证系统使用的模型类，替代掉django提供给我们的用户表auth_user
AUTH_USER_MODEL = 'user.User'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'tiantianxiansheng',
        'USER':'yutaixin',
        'PASSWORD':'123456',    #远程Mysql密码
        'HOST':'49.232.142.68',    #远程mysql数据库主机Ip
        'PORT':'3306'
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-Hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

#配置静态文件访问路径
STATIC_URL = '/static/'
#设置静态存储路径
STATICFILES_DIRS = [os.path.join(BASE_DIR,'static')]

#配置富文本编辑器
TINYMCE_DEFAULT_CONFIG = {
	'theme':'advanced',
	'width':600,
	'height':400,
	}


#邮件发送的配置
EMIAL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.qq.com'
EMAIL_PORT = 25
#发送邮件的邮箱
EMAIL_HOST_USER = '909369814@qq.com'
#在邮箱中设置的客户端授权码
EMAIL_HOST_PASSWORD = 'tpvlhfcmxwbjbfge'
EMAIL_HOST_USER = '909369814@qq.com'
#收件人看到的发件人
EMAIL_FROM = '天天生鲜<909369814@qq.com>'
EMAIL_USE_TLS = True


#django的缓存配置--redis
#这里的配置是我们安装使用django-redis之后的一个配置
CACHES = {
    'default':{
            'BACKEND':'django_redis.cache.RedisCache',
            'LOCATION':'redis://192.168.1.20:6379/9', #redis服务端的ip端口
            'OPTIONS':{
                'CLIENT_CLASS':'django_redis.client.DefaultClient',
                   }
                }
}

#配置session存储到缓存
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'#将session存到缓存中(即redis）
SESSION_CACHE_ALIAS = 'default'

#配置装饰器login_required()检测到未登录时重定向的url:项目中指向我们的登录页面
LOGIN_URL = '/user/login'

#设置django默认存储类
DEFAULT_FILE_STORAGE = 'utils.fdfs.storage.FDFSStorage'

#设置fastdfs使用的client.conf文件路径
FDFS_CLIENT_CONF = './utils/fdfs/client.conf'

#设置fastdfs存储服务器上nginx的ip和port
FDFS_URL = 'http://49.232.142.68:8888/'