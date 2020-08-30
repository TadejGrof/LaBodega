from django.shortcuts import render
from ..models import Dimenzija, Sestavina, Vnos, Kontejner, Sprememba, Dnevna_prodaja
from ..models import Baza, Zaloga, Cena
from django.shortcuts import redirect
from prodaja.models import Stranka
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
        sestavine = zaloga.sestavina_set.all()
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
        tipi_prodaje = zaloga.tipi_prodaj
        if 'vele_prodaja' in tipi_prodaje:
            cenik = zaloga.cenik('vele_prodaja')
        else:
            cenik = zaloga.cenik('dnevna_prodaja')
        nicelne = request.GET.get('nicelne','true')
        tipi = []
        for tip in zaloga.tipi_sestavin:
            if request.GET.get(tip,"true") == "true":
                tipi.append(tip)
        sestavine = sestavine.values(
            'dimenzija__dimenzija',
            'pk',
            'Y',
            'W',
            'JP',
            'JP50',
            'JP70',
        )
        if nicelne == "false":
            ne_prazne = []
            for sestavina in sestavine:
                for tip in tipi:
                    if sestavina[tip] != 0:
                        ne_prazne.append(sestavina)
                        break
            sestavine = ne_prazne
        cene = {}
        skupno = 0
        vrednost = 0
        for sestavina in sestavine:
            dimenzija = sestavina['dimenzija__dimenzija']
            for tip in tipi:
                stevilo = sestavina[tip]
                cena = cenik[dimenzija][tip]
                skupno += stevilo
                vrednost += cena * stevilo
                if dimenzija in cene:
                    if not tip in cene[dimenzija]:
                        cene[dimenzija].update({tip:stevilo * cena})
                else:
                    cene.update({dimenzija:{tip:stevilo * cena}})
        slovar = {
            'zaloga':zaloga,
            'sestavine':sestavine,
            'tipi':tipi,
            'radius':radius,
            'height':height,
            'width':width,
            'skupno':skupno,
            'nicelne': nicelne,
            'cene':cene,
            'vrednost':vrednost
        }
        return pokazi_stran(request, 'zaloga/zaloga.html', slovar)

@login_required
def pregled_prometa(request,tip,pk):
    if request.method == "GET":
        sestavina = Sestavina.objects.get(pk=pk)
        cene_prodaje = Cena.objects.filter(sestavina=sestavina, prodaja__in = ['dnevna_prodaja','vele_prodaja'], tip=tip)
        danes = datetime.date.today().strftime('%Y-%m-%d')
        pred_mescem =  (datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        zacetek_sprememb = request.GET.get('zacetek_sprememb', pred_mescem)
        konec_sprememb = request.GET.get('konec_sprememb', danes)
        spremembe = sestavina.sprememba_set.filter(baza__datum__gt = zacetek_sprememb, baza__datum__lte=konec_sprememb, tip = tip).order_by('-baza__datum','-baza__cas').select_related('baza')
        #spremembe = sestavina.sprememba_set.filter(tip = tip).order_by('-baza__datum','-baza__cas').select_related('baza')
        zaporedna_stanja = sestavina.vrni_stanja(tip,zacetek_sprememb,konec_sprememb)[::-1]
        zacetek_dp = request.GET.get('zacetek_dp', pred_mescem)  
        konec_dp = request.GET.get('konec_dp', danes)
        zacetek_vp = request.GET.get('zacetek_vp', pred_mescem)
        konec_vp = request.GET.get('konec_vp', danes)
        dp_stevilo, dp_cena = sestavina.prodaja('racun',tip, zacetek_dp, konec_dp)
        vp_stevilo, vp_cena = sestavina.prodaja('vele_prodaja',tip, zacetek_vp, konec_vp)
        slovar = {
            'zaporedna_stanja': zaporedna_stanja,
            'tip': tip,
            'sestavina': sestavina,
            'cene_prodaje':cene_prodaje,
            'spremembe': spremembe,
            'zacetek_sprememb': zacetek_sprememb,
            'zacetek_dp': zacetek_dp,
            'zacetek_vp': zacetek_vp,
            'konec_sprememb': konec_sprememb,
            'konec_dp': konec_dp,
            'konec_vp': konec_vp,
            'dp_stevilo': dp_stevilo,
            'dp_cena': dp_cena,
            'vp_stevilo': vp_stevilo,
            'vp_cena': vp_cena
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
