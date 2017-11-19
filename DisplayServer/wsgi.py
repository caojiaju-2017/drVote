"""
WSGI config for DisplayServer project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os,sys

from django.core.wsgi import get_wsgi_application

from os.path import join,dirname,abspath
 
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# import sys
# sys.path.insert(0,PROJECT_DIR)

# PROJECT_DIR = dirname(dirname(abspath(__file__)))#3
sys.path.insert(0,PROJECT_DIR) # 5

#os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DisplayServer.settings")
os.environ["DJANGO_SETTINGS_MODULE"] = "DisplayServer.settings" 
application = get_wsgi_application()
