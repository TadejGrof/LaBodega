from django.views.generic import TemplateView
from django.forms import formset_factory
from django.forms import ModelForm
from zaloga.models import Stranka


class StrankaForm(ModelForm):
    model = Stranka

StrankaFormSet = formset_factory(StrankaForm)

class PregledStrankView(TemplateView):
    template_name = "pregled/stranke.html"

    def get_context_data(self,**kwargs):
        formset = StrankaFormSet()
        return {"formset":formset}



