from zaloga.models import *
from program.api.forms.forms import ModelForm, ViewModelForm, ViewOnlyModelForm
from program.api.forms.fields import ModelChoiceField
from django.forms import models

class TipForm(ModelForm):
    class Meta:
        model = Tip
        fields = ["kratko","dolgo","barva"]

class DimenzijaForm(ModelForm):
    class Meta:
        model = Dimenzija
        fields = ["dimenzija","radij","sirina","visina","special"]

class SestavinaForm(ModelForm):
    class Meta:
        model = Sestavina
        fields = ["dimenzija","tip"]    

class CenaForm(ModelForm):
    class Meta:
        model = Cena
        fields = ["sestavina","cena"]

class ZaposleniForm(ModelForm):
    class Meta:
        model = Zaposleni
        fields = ["ime","priimek"]

class StrankaForm(ViewOnlyModelForm):
    podjetje = ModelChoiceField(queryset=Podjetje.objects.all().filter(stranka__isnull=True))

    title = "Nova stranka:"
    
    class Meta:
        model = Stranka
        fields = ["podjetje"]


class DobaviteljForm(ModelForm):
    class Meta:
        model = Dobavitelj
        fields = ["naziv","kontakt","direktor","drzava"]

class DnevnaProdajaForm(ModelForm):
    class Meta:
        model = Dnevna_prodaja
        fields = ["datum","title","tip"]

class InventuraForm(ModelForm):
    class Meta:
        model = Baza
        fields = ["title","datum","skupno_stevilo"]

class VeleProdajaForm(ModelForm):
    class Meta:
        model = Baza
        fields = ["title","datum","skupno_stevilo"]

class RacunForm(ModelForm):
    class Meta:
        model = Baza
        fields = ["title","datum","skupno_stevilo"]

