import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plumbing_shop.settings")

if os.environ.get("VERCEL"):
    import django
    from django.conf import settings
    if not settings.configured:
        django.setup()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
