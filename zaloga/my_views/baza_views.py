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
        data = {
            'action': 'sprememba',
            'pk': str(vnos.pk),
            'stevilo':str(vnos.stevilo),
            'tip': str(vnos.tip),
            'dolgi_tip': str(vnos.get_tip_display()),
            'dimenzija': str(vnos.dimenzija),
            'varna_dimenzija': str(vnos.dimenzija).replace('/','-'),
            'cena':str(vnos.cena),
            'cena_vnosa': str(vnos.skupna_cena),
            'skupna_cena': str(vnos.baza.skupna_cena),
            'skupno_stevilo': str(vnos.baza.skupno_stevilo),
            'koncna_cena': str(vnos.baza.koncna_cena),
            'cena_popusta': str(baza.cena_popusta),
            'cena_prevoza': str(baza.cena_prevoza),
        }
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
        data = {
            'action': 'novo',
            'pk': str(pk),
            'index': index,
            'tip': vnos.tip,
            'dolgi_tip': vnos.get_tip_display(),
            'stevilo': str(vnos.stevilo),
            'cena': str(vnos.cena),
            'dimenzija': str(vnos.dimenzija),
            'varna_dimenzija': str(vnos.dimenzija).replace('/','-'),
            'cena_vnosa': str(vnos.skupna_cena),
            'cena_popusta': str(baza.cena_popusta),
            'cena_prevoza': str(baza.cena_prevoza),
            'skupno_stevilo': str(baza.skupno_stevilo),
            'skupna_cena': str(baza.skupna_cena),
            'koncna_cena': str(baza.koncna_cena),
            'tip_baze': baza.tip
        }
        return JsonResponse(data)

def izbrisi_vnos(request):
    if request.method=="POST":
        pk = int(request.POST.get('pk'))
        vnos = Vnos.objects.get(pk = pk)
        baza = vnos.baza
        pk = vnos.baza.pk
        vnos.delete()
        data = {
            'pk': str(vnos.pk),
            'action': 'izbris',
            'dimenzija':str(vnos.dimenzija),
            'varna_dimenzija': str(vnos.dimenzija).replace('/','-'),
            'tip': vnos.tip,
            'skupno_stevilo': str(baza.skupno_stevilo),
            'cena_popusta': str(baza.cena_popusta),
            'cena_prevoza': str(baza.cena_prevoza),
            'skupna_cena': str(baza.skupna_cena),
            'koncna_cena': str(baza.koncna_cena)
        }
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
        data = {}
        data['cena_popusta'] = str(baza.cena_popusta)
        data['popust'] = str(baza.popust)
        data['koncna_cena'] = str(baza.koncna_cena)
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
        data = {}
        data['cena_prevoza'] = str(baza.cena_prevoza)
        data['prevoz'] = str(baza.prevoz)
        data['koncna_cena'] = str(baza.koncna_cena)
    return JsonResponse(data) 