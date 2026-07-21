from .base import *
from decouple import config

DEBUG = False

ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='*'
).split(',')

#Seguridad de producción
CSRF_COOKIE_SECURE   = True
SESSION_COOKIE_SECURE = True