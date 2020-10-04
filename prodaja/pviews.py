from django.shortcuts import render
from .models import Stranka, Prodaja, Naslov
from zaloga.models import Vnos, Zaloga, Dimenzija, Sestavina, Baza, Cena, Dnevna_prodaja
from django.shortcuts import redirect
import datetime
from django.utils import timezone
from program.models import Program
import json 
from request_funkcije import vrni_dimenzijo, vrni_slovar, pokazi_stran

def cenik(request,baza,zaloga):
    if request.method == "GET":
        zaloga = Zaloga.objects.get(pk = zaloga)
        sestavine = zaloga.sestavina_set.all()
        sestavine = sestavine.prefetch_related('cena_set').filter(cena__prodaja=baza).values(
            'dimenzija__dimenzija',
            'dimenzija__radius',
            'dimenzija__height',
            'dimenzija__width',
            'dimenzija__special',
            'pk',
            'cena',
            'cena__tip',
            'cena__cena',
            'cena__pk')
        slovar = {
            'sestavine':sestavine,
            'tip':baza,
            'zaloga':zaloga,
        }
    return pokazi_stran(request,'prodaja/cenik.html', slovar)

def spremeni_ceno(request, baza):
    try:
        nova_cena = float(request.POST.get('cena'))
        pk = int(request.POST.get('pk'))
        cena = Cena.objects.get(pk = pk)
        cena.cena = nova_cena
        cena.save()
        data = {}
        data['cena'] = str(cena.cena)
    except:
        pass
    return redirect('cenik_prodaje', baza=baza)

def spremeni_cene(request,baza):
    if request.method == "POST":
        for cena in Cena.objects.filter(prodaja=baza).all():
            nova_cena = request.POST.get('cena_' + str(cena.pk))
            if nova_cena and nova_cena != '':
                nova_cena = float(nova_cena)
                cena.cena = nova_cena
                cena.save()
    return redirect('cenik_prodaje', baza=baza)

###########################################################################################
###########################################################################################
###########################################################################################

def porocilo(request):
    danes = datetime.date.today().strftime('%Y-%m-%d')
    pred_mescem =  (datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    zacetek = request.GET.get('zacetek', pred_mescem)
    konec = request.GET.get('konec', danes)
    
