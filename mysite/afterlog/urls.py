from django.urls import path

from .views import aggregateView, homePageView, downloadView, mailView, transferView

urlpatterns = [

    path('download/<str:couponid>', downloadView, name='download'), 
    path('mail/', mailView, name='mail'),
    path('transfer/',transferView, name = 'transfer'),
    path('aggregate/',aggregateView, name = 'aggregate'),
    path('', homePageView, name='home')]

