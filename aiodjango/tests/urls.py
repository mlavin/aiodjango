from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^ok/', views.normal_ok, name='wsgi-ok'),
    url(r'^async-ok/', views.coroutine_ok, name='aiohttp-ok'),
]
