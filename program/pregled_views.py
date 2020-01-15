from django.shortcuts import render
from zaloga.models import Zaloga, Dnevna_prodaja
from django.contrib.auth.decorators import login_required
from prodaja.models import Prodaja
from django.shortcuts import redirect
from .models import Program
import json 
import datetime

@login_required
def pregled_zalog(request):
    if request.method == "GET":
        zaloge = Zaloga.objects.all()
        return pokazi_stran(request, 'pregled/pregled_zalog.html',{'zaloge':zaloge})

def pregled_zaloge(request, pk):
    zaloga = Zaloga.objects.get(pk = pk)
    slovar = {
        'zaloga':zaloga,
        'pk':pk
    }
    return pokazi_stran(request,'pregled/zaloga.html',slovar)

def sprememba_zaloge(request, pk):
    if request.method == "POST":
        title = request.POST.get('title')
        zaloga = Zaloga.objects.get(pk=pk)
        zaloga.title = title
        zaloga.save()
    return redirect('pregled_zaloge', pk=pk)
###############################################################################################
###############################################################################################

def vrni_slovar(request):
    with open('slovar.json') as dat:
        slovar = json.load(dat)
    return slovar

def pokazi_stran(request, html, baze={}):
    slovar = {'slovar':vrni_slovar(request),'jezik':request.user.profil.jezik}
    slovar.update(baze)
    if not 'zaloga' in baze:
        slovar.update({'zaloga':Zaloga.objects.first()})
    slovar.update({'zaloga_pk':slovar['zaloga'].pk})
    return render(request, html, slovar)