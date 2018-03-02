from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from . import views

app_name = 'course'
urlpatterns = [
    url(r'^classes/?$', views.classes, name='classes'),
    url(r'^([^/]+)/([^/]+)/?$', views.home, name='home'),
    url(r'^([^/]+)/([^/]+)/assignments/?([\d]+)?/?$', views.assignments, name='assignments'),
    url(r'^$', views.index, name='index'),
]