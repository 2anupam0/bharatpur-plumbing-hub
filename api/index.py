import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plumbing_shop.settings")

os.makedirs(os.path.join(BASE_DIR, "staticfiles"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "media"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "media", "products"), exist_ok=True)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
