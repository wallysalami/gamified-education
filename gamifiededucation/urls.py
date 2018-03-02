"""gamifiededucation URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from course.forms.forms import CaptchaPasswordResetForm

from course import views

urlpatterns = [
    url(r'^admin/?', admin.site.urls),
    url(r'^login/?$', views.login, name='login'),
    url(r'^logout/?$', auth_views.logout, name='logout'),
    url(r'', include('course.urls')),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.EMAIL_HOST != '':
    urlpatterns += [
        url(
            r'^password_reset/$',
            auth_views.password_reset,
            {
                'password_reset_form': CaptchaPasswordResetForm,
                'html_email_template_name': 'registration/password_reset_email.html'
            },
        ),
        url(r'', include('django.contrib.auth.urls')),
    ]

handler404 = 'course.views.error_page'
handler500 = 'course.views.error_page'
handler403 = 'course.views.error_page'
handler400 = 'course.views.error_page'