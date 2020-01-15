from django.urls import include,path
from . import views, pregled_views
from zaloga import pdf_views

pregled_zalog_patterns = [
        path('',pregled_views.pregled_zalog, name="pregled_zalog"),
        path('ogled/<int:pk>/',pregled_views.pregled_zaloge, name="pregled_zaloge"),
        path('ogled/<int:pk>/sprememba_zaloge/',pregled_views.sprememba_zaloge, name="sprememba_zaloge"),
]

pregled_zaposlenih_patterns = [
    path('',pregled_views.pregled_zaposlenih, name="pregled_zaposlenih"),
    path('nov_zaposleni/', pregled_views.nov_zaposleni, name="nov_zaposleni"),
    path('ogled/<int:pk>/',pregled_views.pregled_zaposlenega, name="pregled_zaposlenega"),
    path('ogled/<int:pk>/sprememba_zaposlenega/',pregled_views.spremembna_zaposlenega,name="sprememba_zaposlenega"),
]

pregled_strank_patterns = [
    path('', pregled_views.pregled_strank, name='pregled_strank'),
    path('nova_stranka/', pregled_views.nova_stranka, name='nova_stranka'),
    path('ogled_stranke/<int:pk>/',pregled_views.ogled_stranke, name="ogled_stranke"),
    path('spremembna_stranke/<int:pk>/', pregled_views.spremembna_stranke, name='sprememba_stranke'),
    path('izbris_stranke/<int:pk>/', pregled_views.izbris_stranke, name='izbris_stranke'),
]

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('pregled_zalog/', include(pregled_zalog_patterns)),
    path('pregled_zaposlenih/', include(pregled_zaposlenih_patterns)),
    path('pregled_strank/', include(pregled_strank_patterns)),
    path('ponastavi_zalogo/', views.ponastavi_zalogo, name='ponastavi_zalogo'),
    path('spremeni_jezik/', views.spremeni_jezik, name='spremeni_jezik'),
]