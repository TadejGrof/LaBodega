from django import forms

class DodajDimenzijo(forms.Form):
    dimenzija = forms.CharField(required=True, label="Dimenzija")
    radius = forms.CharField(required=True, label="Radius")
    height = forms.Charfield(required=True, label="Height")
    width = forms.Charfiled(required=True, label="Width")
    special = forms.BooleanField()

