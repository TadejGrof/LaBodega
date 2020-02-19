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

@login_required
def skupen_pregled_narocil(request, zaloga):
    zaloga = Zaloga.objects.get(pk = zaloga)
    baze = Baza.objects.filter(status="aktivno", tip="vele_prodaja")
    gledane = request.GET.get('gledane','all')
    ostalo = False
    try:
        gledane = json.loads(gledane)
        if len(gledane) != baze.count():
            ostalo = True
    except:
        gledane = [baza['pk'] for baza in baze.values('pk')]    
    ostala_narocila = baze.exclude(pk__in = gledane).values('pk','stranka__ime')
    narocila = baze.filter(pk__in = gledane).values('pk','stranka__ime','stranka__pk')
    vnosi = Vnos.objects.filter(baza__in = baze).order_by('dimenzija').values('baza__pk','dimenzija__dimenzija','tip','stevilo','pk','baza__stranka__pk')
    razlicne_dimenzije = {}
    for vnos in vnosi:
        dimenzija_tip = vnos['dimenzija__dimenzija'] + '_' + vnos['tip']
        if not vnos['baza__pk'] in gledane:
            stranka = 'ostalo'
        else:
            stranka = vnos['baza__stranka__pk']
        stevilo = vnos['stevilo']
        vnos = vnos['pk']
        if not dimenzija_tip in razlicne_dimenzije:
            if stranka =='ostalo':
                razlicne_dimenzije.update({dimenzija_tip:{stranka:stevilo}})
            else:
                razlicne_dimenzije.update({dimenzija_tip:{stranka:{vnos:stevilo}}})
        elif not stranka in razlicne_dimenzije[dimenzija_tip]:
            if stranka == 'ostalo':
                razlicne_dimenzije[dimenzija_tip].update({stranka:stevilo})
            else:
                razlicne_dimenzije[dimenzija_tip].update({stranka:{vnos:stevilo}})
        else:
            if stranka == "ostalo":
                razlicne_dimenzije[dimenzija_tip][stranka] += stevilo
            else:
                razlicne_dimenzije[dimenzija_tip][stranka].update({vnos:stevilo})
    skupno = {}
    for dimenzija in razlicne_dimenzije:
        skupno.update({dimenzija:0})
        for stranka in razlicne_dimenzije[dimenzija]:
            if stranka != 'ostalo':
                for vnos in razlicne_dimenzije[dimenzija][stranka]:
                    skupno[dimenzija] += razlicne_dimenzije[dimenzija][stranka][vnos]
            else:
                skupno[dimenzija] += razlicne_dimenzije[dimenzija][stranka]
    slovar = {
        'narocila':narocila,
        'ostala_narocila':ostala_narocila,
        'razlicne_dimenzije':razlicne_dimenzije,
        'zaloga':zaloga,
        'skupno':skupno,
        'stevilo_narocil':baze.count(),
        'top': int(request.GET.get('top',0)),
        'ostalo':ostalo,
        'gledane':json.dumps(gledane),
        }
    return pokazi_stran(request,'zaloga/skupen_pregled_narocil.html', slovar ) 


def spremeni_vnos(request, zaloga):
    if request.method=="POST":
        pk = int(request.POST.get('pk'))
        stevilo = int(request.POST.get('stevilo'))
        vnos = Vnos.objects.get(pk = pk)
        vnos.stevilo = stevilo
        vnos.save()
    return JsonResponse({})

def nov_vnos(request,zaloga):
    if request.method == "POST":
        dimenzija = request.POST.get('dimenzija')
        stevilo = int(request.POST.get('stevilo'))
        tip = request.POST.get('tip')
        pk = int(request.POST.get('pk'))
        baza = Baza.objects.get(pk = pk)
        vnos = Vnos.objects.create(
            dimenzija = Dimenzija.objects.get(dimenzija=dimenzija),
            stevilo = stevilo,
            tip = tip,
            cena = Sestavina.objects.get(zaloga=zaloga,dimenzija__dimenzija=dimenzija).cena('vele_prodaja',tip),
            baza = baza)
        pk = vnos.pk
        return JsonResponse({'pk':str(pk)})

def izbrisi_vnos(request,zaloga):
    if request.method=="POST":
        pk = int(reque  st.POST.get('pk'))
        vnos = Vnos.objects.get(pk = pk)
        pk = vnos.baza.pk
        vnos.delete()
        data = {'pk':pk}
    return JsonResponse(data)
    
