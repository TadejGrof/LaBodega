from django.shortcuts import render
from ..models import Dimenzija, Sestavina, Vnos, Kontejner, Sprememba, Dnevna_prodaja
from ..models import Baza, Zaloga, Cena
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import json 
from .. import funkcije
from request_funkcije import pokazi_stran, vrni_dimenzijo, vrni_slovar
from django.urls import reverse
from django.http import JsonResponse

def spremeni_vnos(request):
    if request.method=="POST":
        stevilo = request.POST.get('stevilo')
        cena = request.POST.get('cena')
        tip = request.POST.get('tip')
        vnos = Vnos.objects.get(pk = int(request.POST.get('pk')))
        if stevilo and stevilo != "":
            vnos.stevilo = int(stevilo)
        if tip and tip != "" :
            vnos.tip = tip
        if cena and cena != "" :
            vnos.cena = float(cena)
        vnos.save()
        baza = vnos.baza
        data = podatki_vnosa(vnos)
        data.update(podatki_baze(baza))
        data.update({'action':'sprememba'})
    return JsonResponse(data)

def nov_vnos(request):
    if request.method == "POST":
        dimenzija = vrni_dimenzijo(request)
        stevilo = int(request.POST.get('stevilo'))
        tip = request.POST.get('tip')
        pk = int(request.POST.get('pk'))
        baza = Baza.objects.get(pk = pk)
        zaloga = baza.zaloga
        cena = None
        if baza.tip == "vele_prodaja":
            cena = Sestavina.objects.get(zaloga=zaloga,dimenzija__dimenzija=dimenzija).cena('vele_prodaja',tip)
        elif baza.tip == "racun":
            cena = Sestavina.objects.get(zaloga=zaloga,dimenzija__dimenzija=dimenzija).cena('dnevna_prodaja',tip)
        vnos = Vnos.objects.create(
            dimenzija = dimenzija,
            stevilo = stevilo,
            tip = tip,
            cena = cena,
            baza = baza)
        vnosi = Vnos.objects.all().filter(baza=baza).order_by('dimenzija').values('pk','dimenzija__dimenzija')
        pk = vnos.pk
        index = 0
        for slovar in vnosi:
            if slovar['pk'] == pk:
                break
            index += 1
        data = podatki_vnosa(vnos)
        data.update(podatki_baze(baza))
        data.update({'action':'novo','index':index})
        return JsonResponse(data)

def izbrisi_vnos(request):
    if request.method=="POST":
        pk = int(request.POST.get('pk'))
        vnos = Vnos.objects.get(pk = pk)
        baza = vnos.baza
        pk = vnos.baza.pk
        vnos.delete()
        data = podatki_vnosa(vnos)
        data.update(podatki_baze(baza))
        data.update({'action':'izbris'})
    return JsonResponse(data)
    
def spremeni_popust(request):
    if request.method=="POST":
        pk = int(request.POST.get('pk'))
        baza = Baza.objects.get(pk=pk)
        popust = request.POST.get('popust')
        if popust and popust != "":
            try:
                popust = float(popust)
            except:
                popust = 0
            baza.popust = popust
            baza.save()
        data = podatki_baze(baza)
    return JsonResponse(data) 

def spremeni_prevoz(request):
    if request.method=="POST":
        pk = int(request.POST.get('pk'))
        baza = Baza.objects.get(pk=pk)
        prevoz = request.POST.get('prevoz')
        if prevoz and prevoz != "":
            try:
                prevoz = float(prevoz)
            except:
                prevoz = 0
            baza.prevoz = prevoz
            baza.save()
        data = podatki_baze(baza)
    return JsonResponse(data) 

def vrni_zalogo(request):
    data = {}
    try:
        dimenzija = request.GET.get('dimenzija')
        tip = request.GET.get('tip')
        zaloga = int(request.GET.get('zaloga'))
        stevilo = getattr(Sestavina.objects.all().get(zaloga=zaloga,dimenzija__dimenzija=dimenzija),tip)
        data['zaloga'] = stevilo
    except:
        data['zaloga'] = 0
    return JsonResponse(data)

def podatki_vnosa(vnos):
    data = {}
    data['pk'] = str(vnos.pk)
    data['cena'] = str(vnos.cena)
    data['cena_vnosa'] = str(vnos.skupna_cena)
    data['stevilo'] = str(vnos.stevilo)
    data['dimenzija'] = str(vnos.dimenzija)
    data['varna_dimenzija'] = str(vnos.dimenzija).replace('/','-')
    data['tip'] = vnos.tip
    data['dolgi_tip'] =  vnos.get_tip_display()
    return data

def podatki_baze(baza):
    data = {}
    data['popust'] = str(baza.popust)
    data['cena_popusta'] = str(baza.cena_popusta)
    data['cena_prevoza'] = str(baza.cena_prevoza)
    data['prevoz'] = str(baza.prevoz)
    data['koncna_cena'] = str(baza.koncna_cena)
    data['skupna_cena'] = str(baza.skupna_cena)
    data['skupno_stevilo'] = str(baza.skupno_stevilo)
    return data