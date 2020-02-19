from django.urls import include,path
from .my_views import zaloga_views
from . import views
from .my_views import pdf_views
from .my_views import stroski_views
from .my_views import skupen_pregled_views

ogled_patterns = [
    path('',views.baza, name="baza"),
    path('nov_vnos/', views.nov_vnos, name='baza_nov_vnos'),
    path('iz_datoteke/', views.vnosi_iz_datoteke, name='iz_datoteke'),
    path('shrani_vse/', views.shrani_vse, name='shrani_vse'),
    path('spremeni_vnos/', views.spremeni_vnos, name='baza_spremeni_vnos'),
    path('izbrisi_vnos/', views.izbrisi_vnos, name='baza_izbrisi_vnos'),
    path('izbrisi_vse/',views.izbrisi_vse, name="baza_izbrisi_vse"),
    path('uveljavi/', views.uveljavi_bazo, name='uveljavi_bazo'),
    path('spremeni_popust/', views.spremeni_popust, name='spremeni_popust'),
    path('spremeni_prevoz/', views.spremeni_prevoz, name='spremeni_prevoz'),
    path('pdf/', pdf_views.pdf_baze, name='pdf_baze')
]

baza_patterns = [
    path('', views.baze , name='baze'),
    path('nova_baza/', views.nova_baza, name='nova_baza'),
    path('izbris_baze/<int:pk>/',views.izbris_baze, name='izbris_baze'),
    path('ogled/<int:pk>/', include(ogled_patterns)),
    path('arhiv/', views.arhiv, name='arhiv_baz'),
]

skupen_pregled_patterns = [
    path('', skupen_pregled_views.skupen_pregled_narocil, name="skupen_pregled_narocil"),
    path('spremeni_vnos/',skupen_pregled_views.spremeni_vnos, name='skupen_pregled_spremeni_vnos'),
    path('nov_vnos/', skupen_pregled_views.nov_vnos, name="skupen_pregled_nov_vnos"),
    path('izbrisi_vnos', skupen_pregled_views.izbrisi_vnos, name="skupen_pregled_izbrisi_vnos")
]

strosek_patterns = [
    path('', stroski_views.strosek, name='strosek'),
    path('nov_strosek/', stroski_views.nov_strosek, name="nov_strosek"),
    path('<int:pk>/uveljavi/', stroski_views.uveljavi, name="uveljavi_strosek"),
    path('<int:pk>/nov_vnos/', stroski_views.nov_vnos, name="strosek_nov_vnos"),
    path('<int:pk>/izbris_vnosa/<int:pk_vnosa>/', stroski_views.izbris_vnosa, name="strosek_izbris_vnosa")
]

stroski_patterns = [
    path('',stroski_views.pregled, name='pregled_stroskov'),
]

porocilo_patterns = [
    path('porocilo_prometa',stroski_views.porocilo_prometa, name='porocilo_prometa'),
    path('porocilo_prodaje',stroski_views.porocilo_prodaje, name='porocilo_prodaje'),
]

pregled_patterns = [
    path('', zaloga_views.pregled_prometa,name="pregled_prometa"),
    path('sprememba_cene/<int:cena>/', zaloga_views.sprememba_cene,name="sprememba_cene"),
]

urlpatterns = [
    path('<int:zaloga>/pregled_zaloge/', zaloga_views.pregled_zaloge, name='pregled_zaloge'),
    path('pregled_prometa/<str:tip>/<int:pk>/', include(pregled_patterns)),
    path('<int:zaloga>/pdf/', pdf_views.pdf_zaloge, name='pdf_zaloge'),
    path('dodaj_dimenzijo/', views.dodaj_dimenzijo, name='nova_dimenzija'),
    path('pregled_stroskov/', include(stroski_patterns)),
    path('strosek/', include(strosek_patterns)),
    path('porocilo/',include(porocilo_patterns)),
    path('<int:zaloga>/skupen_pregled_narocil/', include(skupen_pregled_patterns)),
    path('<int:zaloga>/<str:tip_baze>/', include(baza_patterns)),
]