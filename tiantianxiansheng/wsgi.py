"""
WSGI config for tiantianxiansheng project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

#设置django环境变量
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tiantianxiansheng.settings")

application = get_wsgi_application()
