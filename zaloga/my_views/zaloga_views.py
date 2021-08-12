from django.shortcuts import render
from ..models import Dimenzija, Sestavina, Vnos, Kontejner, Dnevna_prodaja, VnosZaloge, Stranka
from ..models import Baza, Zaloga, Cena
from django.shortcuts import redirect
import io
import datetime
from django.contrib.auth.decorators import login_required
import json 
from .. import funkcije
from request_funkcije import pokazi_stran, vrni_dimenzijo, vrni_slovar
from django.urls import reverse

@login_required
def pregled_zaloge(request,zaloga):
    if request.method == "GET":
        zaloga = Zaloga.objects.get(pk = zaloga)
        sestavine = zaloga.sestavine.all()
        radius = request.GET.get('radius','R12')
        height = request.GET.get('height','all')
        width = request.GET.get('width', 'all')
        if radius != "all":
            sestavine = sestavine.filter(dimenzija__radius=radius)
        if height != "all":
            sestavine = sestavine.filter(dimenzija__height=height)
        if width != "all":
            if "C" in width:
                width = width.replace('C','')
                sestavine = sestavine.filter(dimenzija__width=width, dimenzija__special = True)
            else:
                sestavine = sestavine.filter(dimenzija__width=width, dimenzija__special = False)
        nicelne = request.GET.get('nicelne','true')
        rezervirane = request.GET.get('rezervirane','false')
        tipi = []
        for tip in zaloga.tipi_sestavin.all():
            if request.GET.get(tip.kratko,"true") == "true":
                tipi.append(tip.kratko)
        sestavine = sestavine.filter(tip__kratko__in=tipi).all_values().zaloga_values(zaloga)
        if nicelne == "false":
            sestavine = sestavine.exclude(stanje=0)
        dimenzije = Dimenzija.objects.all().values_list('dimenzija','radius','height','width','special')
        slovar = {
            'dimenzije':dimenzije,
            'zaloga':zaloga,
            'sestavine': sestavine,
            'tipi':tipi,
            'radius':radius,
            'height':height,    
            'width':width,
            'nicelne': nicelne,
            'rezervirane': rezervirane,
        }
        return pokazi_stran(request, 'zaloga/zaloga.html', slovar)

@login_required
def pregled_prometa(request,zaloga,sestavina):
    if request.method == "GET":
        zaloga = Zaloga.objects.get(pk=zaloga)
        sestavina = Sestavina.objects.get(pk=sestavina)
        danes = datetime.date.today().strftime('%Y-%m-%d')
        pred_mescem =  (datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        zacetek = request.GET.get('zacetek_sprememb', pred_mescem)
        konec= request.GET.get('konec_sprememb', danes)
        zaporedna_stanja = zaloga.vrni_stanja(sestavina,zacetek,konec)[::-1]
        try:
            if zaporedna_stanja[-1]["tip"] == "inventura":
                zacetno_stanje = zaporedna_stanja[-1]["stanje"]
            else:
                zacetno_stanje = zaporedna_stanja[-1]["stanje"] - zaporedna_stanja[-1]["stevilo"]
        except:
            zacetno_stanje = 0
        try:
            koncno_stanje = zaporedna_stanja[0]["stanje"]
        except:
            koncno_stanje = 0
        slovar = {
            'zacetno_stanje':zacetno_stanje,
            'koncno_stanje':koncno_stanje,
            'spremembe':zaporedna_stanja,
            'sestavina': sestavina,
            'zacetek_sprememb': zacetek,
            'konec_sprememb': konec,
        }
    return pokazi_stran(request, 'zaloga/pregled_prometa.html', slovar)

@login_required
def sprememba_cene(request,tip,pk,cena):
    if request.method=="POST":
        cena = Cena.objects.get(pk = cena )
        cena.cena = float(request.POST.get('cena'))
        cena.save()
    return redirect('pregled_prometa', tip=tip, pk=pk)

@login_required
def dodaj_dimenzijo(request):
    if request.method == "POST":
        dimenzija = request.POST.get('dimenzija')
        radius = request.POST.get('radius')
        height = request.POST.get('height')
        width = request.POST.get('width')
        special = request.POST.get('special')
        if special == "true":
            special = True
        elif special == "false":
            special = False
        Dimenzija.objects.create(
            dimenzija = dimenzija,
            radius = radius,
            height = height,
            width = width,
            special = special)
        return redirect('nova_dimenzija')
    else:
        return pokazi_stran(request, 'zaloga/dodaj_dimenzijo.html')
