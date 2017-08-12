from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from . import views

app_name = 'course'
urlpatterns = [
    url(r'', include('django.contrib.auth.urls')),
    url(r'^courses/', views.courses, name='courses'),
    url(r'(.*)/(.*)/class', views.course_class, name='class'),
    url(r'(.*)/(.*)/me', views.me, name='me'),
    url(r'^$', views.index, name='index'),
]