from django.forms import BaseModelFormSet, modelformset_factory

from zaloga.api.filters.filters import DimenzijaFilter, DobaviteljFilter, SestavinaFilter, StrankaFilter
from .forms import *
from .row_forms import *
from zaloga.models import *
from program.api.forms.formsets import *

class StrankaFormSet(ModelFormSet):
    form = StrankaRowForm
    filter = StrankaFilter
    extra = 0

class DimenzijaFormSet(ModelFormSet):
    form = DimenzijaRowForm
    filter = DimenzijaFilter
    toggle_edit = True

class SestavinaFormSet(ModelFormSet):
    filter = SestavinaFilter
    form = SestavinaRowForm

class DobaviteljFormSet(ModelFormSet):
    form = DobaviteljRowForm
    filter = DobaviteljFilter

class TipFormSet(ModelFormSet):
    form = TipRowForm


