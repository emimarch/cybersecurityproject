from django.urls import path

from .views import homePageView, downloadView, mailView

urlpatterns = [
    path('download/<int:couponid>', downloadView, name='add'),
    path('mail/', mailView, name='mail'),
    path('', homePageView, name='home')]

