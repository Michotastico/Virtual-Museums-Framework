"""DjangoTest URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
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
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import RedirectView

from Apps.CommonWeb.views import IndexView, ContactView
from Apps.CommonWeb.views import LoginView
from Apps.CommonWeb.views import LogoutView
from Apps.Curator.views.opinions import OpinionHashView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^contact/', ContactView.as_view(), name='contact'),
    url(r'^auth/login', LoginView.as_view(), name='login'),
    url(r'^auth/logout', LogoutView.as_view(), name='logout'),
    url(r'^confirmation/', OpinionHashView.as_view(), name='opinion_confirmation'),
    url(r'^curator/', include('Apps.Curator.urls')),
    url(r'^visitor/', include('Apps.Visitor.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/images/museum.ico', permanent=True)),

]
