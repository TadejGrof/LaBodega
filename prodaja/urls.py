from django.urls import include,path
from zaloga import views
from . import pviews 
from zaloga.my_views import pdf_views

dnevna_prodaja_patterns = [
    path('', pviews.dnevna_prodaja, name="dnevna_prodaja"),
    path('nova_prodaja/', pviews.nova_dnevna_prodaja, name="nova_dnevna_prodaja"),
    path('nov_racun/', pviews.nov_racun, name="nov_racun"),
    path('racun/<int:pk>/nov_vnos/', pviews.racun_nov_vnos, name="racun_nov_vnos"),
    path('racun/spremeni_vnos/', pviews.racun_sprememba_vnosa, name="racun_spremeni_vnos"),
    path('racun/izbrisi_vnos/', pviews.racun_izbris_vnosa, name="racun_izbrisi_vnos"),
    path('racun/spremeni_popust/', pviews.racun_spremeni_popust, name="racun_spremeni_popust"),
    path('uveljavi_racun/<int:pk>/', pviews.uveljavi_racun, name="uveljavi_racun"),
    path('arhiv/ogled/<int:pk>/', pviews.ogled_dnevne_prodaje, name='ogled_dnevne_prodaje'),
    path('arhiv/ogled/<int:pk>/pdf/<str:tip>/', pdf_views.pdf_dnevne_prodaje, name='pdf_dnevne_prodaje'),
    path('arhiv/ogled/<int:pk>/storniraj/<int:pk_r>/', pviews.storniraj_racun, name="storniraj_racun"),
]

urlpatterns = [
    path('', pviews.pregled_prodaje, name='pregled_prodaje'),
    path('dnevna_prodaja/', include(dnevna_prodaja_patterns)),
    path('cenik/<str:baza>/', pviews.cenik, name='cenik_prodaje'),
    path('cenik/<str:baza>/spremeni_ceno/', pviews.spremeni_ceno, name='spremeni_ceno'),
    path('cenik/<str:baza>/spremeni_cene/', pviews.spremeni_cene, name='spremeni_cene'),
    path('cenik/<str:tip_prodaje>/pdf/', pdf_views.pdf_cenika, name='cenik_pdf'),
]