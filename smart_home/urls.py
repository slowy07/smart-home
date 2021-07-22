from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.conf import settings

url_patterns = [
    path('admin/', admin.site.urls),
    url(r'^', include(('restLogin.urls', 'restLogin'), namespace = 'rest-login')),
    url(r'^', include(('rooms.urls','rooms'), namespace = 'rooms')),
    url(r'^', include(('raspberry.urls', 'raspberry'), namespace = "raspberry")),
]
if settings.DEBUG:
    url_patterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)