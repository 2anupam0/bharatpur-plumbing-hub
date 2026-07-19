import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "plumbing_shop.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
app = application

_seeded = False

def _check_and_seed():
    global _seeded
    if _seeded:
        return
    _seeded = True
    try:
        from shop.models import Category
        if Category.objects.filter(name="CPVC Pipes").exists():
            return
        from django.core.management import call_command
        call_command("seed_data")
    except Exception:
        pass

try:
    _check_and_seed()
except Exception:
    pass
