from django_filters import FilterSet, CharFilter, ModelChoiceFilter
from program.models import Drzava
from zaloga.models import Tip
from program.api.filters.filters import InitFilterSet

def drzave(request):
    return Drzava.objects.all()

def tipi(request):
    return Tip.objects.all()

class StrankaFilter(FilterSet):
    naziv_podjetja = CharFilter(field_name="podjetje__naziv",lookup_expr='icontains', label="Podjetje")
    drzava = ModelChoiceFilter(field_name="podjetje__drzava", queryset = drzave, label="Drzava")

class DimenzijaFilter(FilterSet):
    dimenzija = CharFilter(field_name="dimenzija", lookup_expr="icontains", label="Dimenzija")

class DobaviteljFilter(FilterSet):
    naziv_podjetja = CharFilter(field_name="podjetje__naziv",lookup_expr='icontains', label="Podjetje")
    drzava = ModelChoiceFilter(field_name="podjetje__drzava", queryset = drzave, label="Drzava")

class SestavinaFilter(FilterSet):
    dimenzija = CharFilter(field_name="dimenzija__dimenzija",lookup_expr='icontains', label="Dimenzija")
    tip = ModelChoiceFilter(field_name="tip__kratko", queryset = tipi, label="Tip")

