from django.urls import include,path
from zaloga import views
from . import pviews 
from zaloga.my_views import pdf_views

urlpatterns = [
    path('cenik/<str:baza>/', pviews.cenik, name='cenik_prodaje'),
    path('cenik/<str:baza>/spremeni_cene/', pviews.spremeni_cene, name='spremeni_cene'),
    path('cenik/<str:tip_prodaje>/pdf/', pdf_views.pdf_cenika, name='cenik_pdf'),
]