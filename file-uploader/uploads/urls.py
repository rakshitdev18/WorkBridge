from hh.views import *
from django.urls import path


urlpatterns = [
    path('', home, name='home'),
    path('sim/', sim, name='sim'),
    path('begin/', begin, name='begin'),
    path('mail/', mail, name='mail'),
    path('works/', works, name='works'),
    path('register/', register, name='register'),
    path('teams/', teams, name='teams'),
    path('ide/', ide, name='ide'),
    path('login/', login, name='login'),
    path('save_message/', save_message, name='save_message'),
    path('chat/', chat_page, name='chat_page'),
    path('roles/', roles, name='roles'),
    path('result/', result, name='result'),
    path('trial/', trial, name='trial'),
]