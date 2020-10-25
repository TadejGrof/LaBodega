from django.urls import include,path
from .my_views import zaloga_views
from . import views
from .my_views import pdf_views
from .my_views import stroski_views
from .my_views import skupen_pregled_views
from .my_views import baza_views
from .my_views import pviews

ogled_patterns = [
    path('',views.baza, name="baza"),
    path('iz_datoteke/', views.vnosi_iz_datoteke, name='iz_datoteke'),
    path('uveljavi/', views.uveljavi_bazo, name='uveljavi_bazo'),
    path('pdf/', pdf_views.pdf_baze, name='pdf_baze'),
    path('pdf/razlika', pdf_views.pdf_razlike, name="pdf_razlike"),
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
    path('pdf/',pdf_views.pdf_skupnega_pregleda,name="pdf_skupnega_pregleda"),
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

cenik_patterns = [
    path('<str:baza>/', pviews.cenik, name='cenik_prodaje'),
    path('<str:baza>/spremeni_cene/', pviews.spremeni_cene, name='spremeni_cene'),
    path('<str:tip_prodaje>/pdf/', pdf_views.pdf_cenika, name='cenik_pdf'),
]
dnevna_prodaja_patterns = [
    path('', pviews.dnevna_prodaja, name="dnevna_prodaja"),
    path('nova_prodaja/', pviews.nova_dnevna_prodaja, name="nova_dnevna_prodaja"),
    path('nov_racun/', pviews.nov_racun, name="nov_racun"),
    path('uveljavi_racun/<int:pk_racuna>/', pviews.uveljavi_racun, name="uveljavi_racun"),
    path('arhiv/ogled/<int:pk_prodaje>/', pviews.ogled_dnevne_prodaje, name='ogled_dnevne_prodaje'),
    path('arhiv/ogled/<int:pk_prodaje>/pdf/<str:tip>/', pdf_views.pdf_dnevne_prodaje, name='pdf_dnevne_prodaje'),
    path('arhiv/ogled/<int:pk_prodaje>/storniraj/<int:pk_racuna>/', pviews.storniraj_racun, name="storniraj_racun"),
]

ajax_patterns = [
    path('spremeni_vnos/', baza_views.spremeni_vnos, name='spremeni_vnos'),
    path('nov_vnos/', baza_views.nov_vnos, name="nov_vnos"),
    path('izbrisi_vnos', baza_views.izbrisi_vnos, name="izbrisi_vnos"),
    path('spremeni_popust/', baza_views.spremeni_popust, name='spremeni_popust'),
    path('spremeni_prevoz/', baza_views.spremeni_prevoz, name='spremeni_prevoz'),
    path('vrni_zalogo/', baza_views.vrni_zalogo, name='vrni_zalogo'),
    path('spremeni_ceno/', baza_views.spremeni_ceno, name='spremeni_ceno'),
    path('vrni_bazo/', baza_views.vrni_bazo,name="vrni_bazo"),
    path('vrni_dimenzijo/', baza_views.vrni_dimenzijo, name="vrni_dimenzijo"),
    path('izbrisi_racun/', baza_views.izbrisi_racun, name="izbrisi_racun")
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
    path('<int:zaloga>/dnevna_prodaja/',include(dnevna_prodaja_patterns)),
    path('<int:zaloga>/cenik/', include(cenik_patterns)),
    path('<int:zaloga>/<str:tip_baze>/', include(baza_patterns)),
    path('ajax/', include(ajax_patterns))
    
]