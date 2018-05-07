"""QCR URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
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
from django.http import HttpResponseRedirect
from django.contrib.auth import views as auth_views

urlpatterns = [
	url(r'^files/', include('db_file_storage.urls')),	
	url(r'^qcr/', include('report.urls')),
	url(r'^manager/', include('manager.urls')),
	url(r'^admin/', admin.site.urls),
	url(r'^login/$', auth_views.login, {'redirect_authenticated_user': True}, name='login'),
	url(r'^$', lambda r: HttpResponseRedirect('login/')),

]