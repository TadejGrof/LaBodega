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
    baze = Baza.objects.filter(zaloga = zaloga, status="aktivno", tip="vele_prodaja")
    narocila = baze.values('pk','stranka__ime','stranka__pk')
    vnosi = Vnos.objects.filter(baza__in = baze).order_by('dimenzija').values('baza__pk','dimenzija__dimenzija','dimenzija__radius','tip','stevilo','pk','baza__stranka__pk')
    razlicne_dimenzije = {}
    for vnos in vnosi:
        dimenzija = vnos['dimenzija__dimenzija']
        tip = vnos['tip']
        dimenzija_tip = dimenzija + '_' + tip
        radius = vnos['dimenzija__radius']
        stevilo = vnos['stevilo']
        baza = vnos['baza__pk']
        vnos = vnos['pk']
        if not dimenzija_tip in razlicne_dimenzije:
            razlicne_dimenzije[dimenzija_tip] = {'dimenzija':dimenzija,'radius':radius,'tip':tip,'baze':{baza:{vnos:stevilo}}}
        elif not baza in razlicne_dimenzije[dimenzija_tip]['baze']:
            razlicne_dimenzije[dimenzija_tip]['baze'][baza] = {vnos:stevilo}
        else:
            razlicne_dimenzije[dimenzija_tip]['baze'][baza][vnos] = stevilo
    slovar = {
        'narocila':narocila,
        'razlicne_dimenzije':razlicne_dimenzije,
        'na_voljo': zaloga.dimenzija_tip_zaloga,
        }

    return pokazi_stran(request,'zaloga/skupen_pregled_narocil.html', slovar ) 


