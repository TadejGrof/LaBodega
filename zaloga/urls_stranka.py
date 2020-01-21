from django.urls import include,path
from . import stranka_views

urlpatterns = [
    path('pregled/', stranka_views.pregled_narocil, name='stranka_pregled_narocil'),
    path('pregled/novo_narocilo/', stranka_views.novo_narocilo, name="stranka_novo_narocila"),
    path('pregled/ogled_narocila/<int:pk>/', stranka_views.ogled_narocila, name="stranka_ogled_narocila"),
    path('zgodovina/', stranka_views.zgodovina, name="stranka_zgodovina")
]


