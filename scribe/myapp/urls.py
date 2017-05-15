__author__ = 'cc'
from django.conf.urls import url,include
from django.contrib import admin
from . import views

urlpatterns = [
    url(r'^myapp/login/',views.login_view,name = 'login'),
    url(r'myapp/auth/',views.authorize_user,name ='auth'),
    url(r'myapp/oauth2callback/',views.oauth2callback,name ='oauthcallback'),
    url(r'^myapp/$', views.index, name='index'),
    url(r'^', views.sales_form)
]
