from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('ponastavi_zalogo/', views.ponastavi_zalogo, name='ponastavi_zalogo'),
    path('spremeni_jezik/', views.spremeni_jezik, name='spremeni_jezik'),
]