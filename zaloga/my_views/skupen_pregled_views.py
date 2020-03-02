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
    narocila = baze.values('pk','stranka__ime','stranka__pk')
    vnosi = Vnos.objects.filter(baza__in = baze).order_by('dimenzija').values('baza__pk','dimenzija__dimenzija','tip','stevilo','pk','baza__stranka__pk')
    razlicne_dimenzije = {}
    for vnos in vnosi:
        dimenzija_tip = vnos['dimenzija__dimenzija'] + '_' + vnos['tip']
        stevilo = vnos['stevilo']
        baza = vnos['baza__pk']
        vnos = vnos['pk']
        if not dimenzija_tip in razlicne_dimenzije:
            razlicne_dimenzije[dimenzija_tip] = {baza:{vnos:stevilo}}
        elif not baza in razlicne_dimenzije[dimenzija_tip]:
            razlicne_dimenzije[dimenzija_tip][baza] = {vnos:stevilo}
        else:
            razlicne_dimenzije[dimenzija_tip][baza][vnos] = stevilo
    skupno = {}
    for dimenzija in razlicne_dimenzije:
        sestevek = 0
        for baza in razlicne_dimenzije[dimenzija]:
            for vnos in razlicne_dimenzije[dimenzija][baza]:
                sestevek += razlicne_dimenzije[dimenzija][baza][vnos]
        skupno[dimenzija] = sestevek
    slovar = {
        'narocila':narocila,
        'razlicne_dimenzije':razlicne_dimenzije,
        'na_voljo': zaloga.dimenzija_tip_zaloga,
        'skupno':skupno
        }
    return pokazi_stran(request,'zaloga/skupen_pregled_narocil.html', slovar ) 


