from django.urls import path

from .views import homePageView, downloadView, mailView, transferView

urlpatterns = [
    path('download/<int:couponid>', downloadView, name='add'),
    path('mail/', mailView, name='mail'),
    path('transfer/',transferView, name = 'transfer'),
    path('', homePageView, name='home')]

