from program.api.views.viewsets import ModelListViewSet
from zaloga.api.filters.filters import StrankaFilter
from zaloga.models import Stranka
from zaloga.api.forms.forms import *
from zaloga.api.forms.formsets import *
from zaloga.api.filters.filters import *

class StrankaViewSet(ModelListViewSet):
    model = Stranka
    formset = StrankaFormSet

    list_view_title = "Pregled strank:"

class DimenzijaViewSet(ModelListViewSet):
    model = Dimenzija
    formset = DimenzijaFormSet

    list_view_title = "Pregled dimenzij:"

class DobaviteljViewSet(ModelListViewSet):
    model = Dobavitelj
    formset = DobaviteljFormSet

    list_view_title = "Pregled dobaviteljev:"

class SestavinaViewSet(ModelListViewSet):
    model = Sestavina
    formset = SestavinaFormSet
    list_view_title = "Pregled sestavin:"

    def _get_queryset(self,request=None):
        return Sestavina.objects.none()


