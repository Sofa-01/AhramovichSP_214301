import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.api.settings')
django.setup()