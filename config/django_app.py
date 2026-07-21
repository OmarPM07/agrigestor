import os
import django

"""
def setup_django():
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE',
        'config.settings.development'
    )
    django.setup()
"""    
def setup_django():
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE',
        'config.settings.production'
    )
    django.setup()