from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from shop.views import setup_database

def serve_media(request, path):
    return serve(request, path, document_root=settings.MEDIA_ROOT)

urlpatterns = [
    path("setup/", setup_database, name="setup_database"),
    path("admin/", include("shop.admin_panel_urls")),
    path("dashboard/", include("shop.owner_urls")),
    path("", include("shop.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    re_media = r'^media/(?P<path>.*)$'
    urlpatterns += [re_path(re_media, serve_media)]
