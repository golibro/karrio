"""
purplship server core module urls
"""
from django.urls import include, path
from purplship.server.core.views import metadata, router

app_name = "purplship.server.core"
urlpatterns = [
    path("", metadata.view),
    path("v1/", include(router.urls)),
]
