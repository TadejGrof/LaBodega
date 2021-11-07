from django.utils import text
from zaloga.models import Tip
from django.forms import ModelForm
from django.db.models.fields.related import ForeignKey
from django.forms.models import BaseModelFormSet, BaseModelForm, ModelChoiceIterator, ModelChoiceField, ModelFormMetaclass, ModelFormOptions
from django.forms.fields import Field


class TipModel(ModelForm):
    class Meta:
        model = Tip
        fields = ["dolgo","kratko","barva"]

