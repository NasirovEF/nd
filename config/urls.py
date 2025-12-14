from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("organization.urls", namespace="organization")),
    path("", include("learning.urls", namespace="learning")),
    path("", include("accident.urls", namespace="accident")),
    path("", include("users.urls", namespace="users")),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
