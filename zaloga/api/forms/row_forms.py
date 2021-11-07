from zaloga.models import *
from program.api.forms.forms import RowModelForm

class TipRowForm(RowModelForm):
    class Meta:
        model = Tip
        fields = ["kratko","dolgo","barva"]

class DimenzijaRowForm(RowModelForm):
    class Meta:
        model = Dimenzija
        fields = ["dimenzija","radij","sirina","visina","special"]

class SestavinaRowForm(RowModelForm):
    class Meta:
        model = Sestavina
        fields = ["naziv_dimenzije","kratek_tip"]    

class CenaRowForm(RowModelForm):
    class Meta:
        model = Cena
        fields = ["sestavina","cena"]

class ZaposleniRowForm(RowModelForm):
    class Meta:
        model = Zaposleni
        fields = ["ime","priimek","položaj","kontakt"]

class StrankaRowForm(RowModelForm):
    class Meta:
        model = Stranka
        fields = ["naziv","kontakt","direktor","drzava"]

class DobaviteljRowForm(RowModelForm):
    class Meta:
        model = Dobavitelj
        fields = ["naziv","kontakt","direktor","drzava"]

class DnevnaProdajaRowForm(RowModelForm):
    class Meta:
        model = Dnevna_prodaja
        fields = ["datum","title","tip"]

class InventuraRowForm(RowModelForm):
    class Meta:
        model = Baza
        fields = ["title","datum","skupno_stevilo"]

class VeleProdajaRowForm(RowModelForm):
    class Meta:
        model = Baza
        fields = ["title","datum","skupno_stevilo"]

class RacunRowForm(RowModelForm):
    class Meta:
        model = Baza
        fields = ["title","datum","skupno_stevilo"]

