from django.urls import include, path
# import routers
from rest_framework import routers
  
# import everything from views
from .viewsets import *
from .views import *
# define the router
router = routers.DefaultRouter()
  
# define the router path and viewset to be used
router.register(r'dimenzija', DimenzijaViewSet)
router.register(r'tip', TipViewSet)
router.register(r'sestavina',SestavinaViewSet)
router.register(r'baza',BazaViewSet)
# specify URL Path for rest_framework

api_patterns = [
    path('', include(router.urls)),
    path("baza/uveljavi/", BazaView.as_view())
    #path('api-auth/', include('rest_framework.urls'))]
]

web_patterns = [
    path("poslovne_enote/", poslovne_enote, name="poslovne_enote"),
    path("poslovna_enota/<int:poslovna_enota_pk>/", poslovna_enota, name="poslovna_enota"),
    path("poslovna_enota/<int:poslovna_enota_pk>/zaloga/<int:zaloga_pk>/", zaloga, name="zaloga")
]


urlpatterns = [
    path('', include(web_patterns)),
    path('api/', include(api_patterns)),
    
]