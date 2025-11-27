from django.contrib import admin
from django.urls import path
from authentication.views import *
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

# Define URL patterns
urlpatterns = [
    path('home/', home, name='home'),
    path('admin/', admin.site.urls),
    path('login/', login_page, name='login_page'),
    path('register/', register_page, name='register_page'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()