from django.shortcuts import render
from ..models import Dimenzija, Sestavina, Vnos, Kontejner, Dnevna_prodaja, Tip, VnosZaloge
from ..models import Baza, Zaloga, Cena
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import json 
from .. import funkcije
from request_funkcije import pokazi_stran, vrni_slovar
from request_funkcije import vrni_dimenzijo as dimenzija_iz_requesta
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST,require_GET

@require_POST
def spremeni_vnos(request):
    try:
        stevilo = request.POST.get('stevilo', None)
        cena = request.POST.get('cena', None)
        tip = request.POST.get('tip', None)
        vnos = Vnos.objects.get(pk = int(request.POST.get('vnos')))
        if stevilo and stevilo != "":
            vnos.stevilo = int(stevilo)
        if tip and tip != "" :
            tip = Tip.objects.get(id=tip)
            vnos.tip = tip
        if cena and cena != "" :
            vnos.cena = float(cena)
        vnos.save()
        data = {
            "vnos": vnos.all_values(),
            "baza": vnos.baza.all_values(),
            "action":"sprememba",
            "success":True,
        }
    except:
        data = {"success":False}
    return JsonResponse(data)

@require_POST
def nov_vnos(request):
    try:
        stevilo = int(request.POST.get('stevilo'))
        sestavina = Sestavina.objects.get(pk=request.POST.get('sestavina'))
        baza = Baza.objects.get(pk = int(request.POST.get('baza')))
        zaloga = baza.zaloga
        cena = None
        if baza.tip == "vele_prodaja" or baza.tip == "racun":
            cena = zaloga.cenik.get(sestavina)
        vnos = Vnos.objects.create(
            sestavina = sestavina,
            stevilo = stevilo,
            cena = cena,
            baza = baza)
        index = 1
        for v in baza.vnos_set.all().order_by("sestavina").values("id"):
            if vnos.id == v["id"]:
                break
            index += 1
        vnos_values = vnos.all_values()
        vnos_values["index"] = index
        data = {
            "vnos": vnos_values,
            "baza": vnos.baza.all_values(),
            "action":"novo",
            "success":True,
        }
    except:
        data = {"success":False}
    return JsonResponse(data)

@require_POST
def izbrisi_vse(request):
    try:
        baza = Baza.objects.get(pk=request.POST.get("baza"))
        baza.vnos_set.all().delete()
        data = {
            "baza":baza.all_values(),
            "success":True
        }
    except:
        data = {"success":False}
    return JsonResponse(data)

@require_POST
def izbrisi_vnos(request):
    try:       
        vnos = Vnos.objects.get(pk = int(request.POST.get('vnos')))
        vnos_values = {"id":vnos.id}
        baza = vnos.baza
        vnos.delete()
        data = {
            "vnos":vnos_values,
            "baza": baza.all_values(),
            "action":"izbris",
            "success":True
        }
    except:
        data = {"success": False}
    return JsonResponse(data)

@require_POST
def spremeni_baza_value(request):
    try:
        baza = Baza.objects.get(pk=int(request.POST.get('baza')))
        setattr(baza,request.POST.get("sprememba"),request.POST.get("value"))
        baza.save()
        data = {
            "baza":baza.all_values(),
            "success":True
        }
    except:
        data = {"success":False}
    return JsonResponse(data) 

def spremeni_ceno(request):
    data = {}
    if request.method == "POST":
        try:
            pk = int(request.POST.get('pk'))
            nova_cena = float(request.POST.get('cena'))
            cena = Cena.objects.get(pk = pk)
            cena.cena = nova_cena
            cena.save()
            data['cena'] = str(nova_cena)
        except:
            data['cena'] = 0
    return JsonResponse(data)

def izbrisi_racun(request):
    data = {}
    if request.method == "POST":
        pk = int(request.POST.get('pk'))
        racun = Baza.objects.get(pk = pk)
        prodaja = racun.dnevna_prodaja
        print(prodaja)
        racun.delete()
        print('po')
        data['skupno_stevilo'] = prodaja.skupno_stevilo
        print('po')
        data['skupna_cena'] = prodaja.skupna_cena
        print('po')
    return JsonResponse(data) 


