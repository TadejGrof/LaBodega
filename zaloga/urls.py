from django.urls import include,path
from . import views
from . import pdf_views

ogled_patterns = [
    path('',views.baza, name="baza"),
    path('nov_vnos/', views.nov_vnos, name='baza_nov_vnos'),
    path('iz_datoteke/', views.vnosi_iz_datoteke, name='iz_datoteke'),
    path('shrani_vse/', views.shrani_vse, name='shrani_vse'),
    path('spremeni_vnos/', views.spremeni_vnos, name='baza_spremeni_vnos'),
    path('izbrisi_vnos/', views.izbrisi_vnos, name='baza_izbrisi_vnos'),
    path('uveljavi/', views.uveljavi_bazo, name='uveljavi_bazo'),
    path('spremeni_popust/', views.spremeni_popust, name='spremeni_popust'),
    path('pdf/', pdf_views.pdf_baze, name='pdf_baze')
]

baza_patterns = [
    path('', views.baze , name='baze'),
    path('nova_baza/', views.nova_baza, name='nova_baza'),
    path('izbris_baze/<int:pk>/',views.izbris_baze, name='izbris_baze'),
    path('ogled/<int:pk>/', include(ogled_patterns)),
    path('arhiv/', views.arhiv, name='arhiv_baz'),
]


urlpatterns = [
    path('', views.pregled_zaloge, name='pregled_zaloge'),
    path('pregled_prometa/', views.pregled_prometa, name='pregled_prometa'),
    path('pdf/', pdf_views.pdf_zaloge, name='pdf_zaloge'),
    path('dodaj_dimenzijo/', views.dodaj_dimenzijo, name='nova_dimenzija'),
    path('iz_datoteke', views.sestavine_iz_datoteke, name="sestavine_iz_datoteke"),
    path('<str:tip_baze>/', include(baza_patterns)),
]