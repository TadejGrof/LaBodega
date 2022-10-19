# import viewsets
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework import status
from rest_framework.response import Response

# import local data
from .serializers import *
from .models import *
  
# create a viewset
class DimenzijaViewSet(viewsets.ModelViewSet):
    # define queryset
    queryset = Dimenzija.objects.all()
      
    # specify serializer to be used
    serializer_class = DimenzijaSerializer

class TipViewSet(viewsets.ModelViewSet):
    # define queryset
    queryset = Tip.objects.all()
      
    # specify serializer to be used
    serializer_class = TipSerializer

class SestavinaViewSet(viewsets.ModelViewSet):
    # define queryset
    queryset = Sestavina.objects.all()
      
    # specify serializer to be used
    serializer_class = SestavinaSerializer

class BazaViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Baza.objects.all()
      
    # specify serializer to be used
    serializer_class = BazaSerializer
    
    def uveljavi(self,request,*args,**kwargs):
        baza = self.get_object()
        baza.uveljavi()

        return Response(self.serializer_class(baza))

class InventuraViewSet(viewsets.ModelViewSet):
    queryset = Baza.objects.all().filter(tip="inventura")

    serializers = BazaSerializer


class VnosViewSet(viewsets.ModelViewSet):
    queryset = VnosBaze.objects.all()

    serializer_class = VnosBazeSerializer

