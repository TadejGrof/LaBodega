from django.urls import include,path
from . import views, pregled_views
from zaloga import pdf_views

pregled_zalog_patterns = [
        path('',pregled_views.pregled_zalog, name="pregled_zalog"),
        path('ogled/<int:pk>/',pregled_views.pregled_zaloge, name="pregled_zaloge"),
        path('ogled/<int:pk>/sprememba_zaloge/',pregled_views.sprememba_zaloge, name="sprememba_zaloge"),
]

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('pregled_zalog/', include(pregled_zalog_patterns)),
    path('ponastavi_zalogo/', views.ponastavi_zalogo, name='ponastavi_zalogo'),
    path('spremeni_jezik/', views.spremeni_jezik, name='spremeni_jezik'),
]