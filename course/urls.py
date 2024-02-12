from django.urls import re_path, include
from django.contrib.auth import views as auth_views

from . import views

app_name = 'course'
urlpatterns = [
    re_path(r'^classes/?$', views.classes, name='classes'),
    re_path(r'^([^/]+)/([^/]+)/?$', views.home, name='home'),
    re_path(r'^([^/]+)/([^/]+)/assignments/?([\d]+)?/?$', views.assignments, name='assignments'),
    re_path(r'^$', views.index, name='index'),
]