"""IssuesHub_Bilby URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.urls import path, include
from django.contrib.auth.views import login, logout

from . import views

#
urlpatterns = [
    url(r'^$', views.index, name='index'),
    path("insightMap/", views.kumu, name='kumu'),
    path("insightMap/blueprint.json", views.blueprint, name='blueprint'),
    path("insightMap/index", views.mapIndex, name='mapIndex'),
    path("login/", login, {'template_name': 'home/login.html'}, name='login'),
    path("logout/", logout, {'template_name': 'home/logout.html'}, name='logout'),
    path("register/", views.register, name="register"),
    path("profile/", views.profileChange, name='profile'),
    path("password/", views.passwordChange, name="passwordChange"),
    path("registerInterest/", views.interestsChange, name='interestChange'),
    path("userReport/", views.userReport, name='userReport'),
]
