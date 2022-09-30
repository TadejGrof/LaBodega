import io
from datetime import datetime
import json
import os
import shutil
from program.models import Program
from zaloga.models import Zaloga, Dimenzija
from prodaja.models import Stranka
import json
from django.db.models import F
from zaloga.models import Vnos

import random

def random_color():
    r = random.randint(0,255)
    g = random.randint(0,255)
    b = random.randint(0,255)
    return [r,g,b]

def vnosi_iz_filtra(filter,zaloga,od_datum,do_datum):
    tipi, dimenzija_filter = seperate_filter(filter)
    dimenzije = filtriraj_dimenzije(dimenzija_filter)
    vnosi = Vnos.objects.filter(tip__in = tipi, dimenzija__in = [d["id"] for d in dimenzije],baza__zaloga=zaloga, baza__tip="racun", baza__status="veljavno", baza__dnevna_prodaja__datum__gte = od_datum, baza__dnevna_prodaja__datum__lte = do_datum).values(
        "dimenzija__dimenzija", "stevilo", "tip","cena","baza__dnevna_prodaja__datum"
    ).order_by("baza__dnevna_prodaja__datum")
    return vnosi

def vnosi_iz_filtra(filter,zaloga):
    tipi, dimenzija_filter = seperate_filter(filter)
    dimenzije = filtriraj_dimenzije(dimenzija_filter)
    return Vnos.objects.filter(tip__in = tipi, dimenzija__in = [d["id"] for d in dimenzije],baza__zaloga=zaloga)

def filtriraj_dimenzije(filter):
    if isinstance(filter, str):
        split = filter.split(" ")
    elif isinstance(filter, list):
        split = filter
    else:
        print("ERROR")
    dimenzije = Dimenzija.objects.all().values()
    valid_dimenzije = []
    for dimenzija in dimenzije:
        valid = True
        filter_dimenzija = dimenzija["dimenzija"]
        for filter in split:
            if filter not in filter_dimenzija:
                valid = False
                break
            else:
                if filter + "/" in filter_dimenzija:
                    filter_dimenzija = filter_dimenzija.replace(filter + "/", "",1)
                else:
                    filter_dimenzija = filter_dimenzija.replace(filter,"",1)
        if valid:
            valid_dimenzije.append(dimenzija)
    return valid_dimenzije

def merge_tipe_vnosov(vnosi):
    tipi = ["Y","W","JP70"]
    data = {dimenzija: {tip : 0 for tip in tipi} for dimenzija in razlicne_dimenzije(vnosi)}
    for vnos in vnosi:
        data[vnos["dimenzija"]][vnos["tip"]] += vnos["stevilo"]
    for key,value in data.items():
        data[key]["skupno"] = value["Y"] + value["W"] + value["JP70"]
        data[key]["dimenzija"] = key
    return data.values()

def razlicne_dimenzije(vnosi):
    slovar = {}
    for vnos in vnosi:
        slovar[vnos["dimenzija"]] = True
    return slovar.keys()

def analiza_narocil(request,zaloga):
    zaloga = Zaloga.objects.get(pk = zaloga)
    query = request.GET.get("query")
    skupina = request.GET.get("skupina")
    if skupina == "all":
        stranke = Stranka.objects.all()
    else:
        stranke = Stranka.objects.filter(skupina = int(skupina))
    vnosi = vnosi_iz_filtra(query,zaloga)
    vnosi = vnosi.filter(baza__tip="narocilo", baza__status="model", baza__stranka__in = stranke).order_by("dimenzija").values("stevilo","dimenzija__dimenzija","tip","cena","baza__stranka")

    sestevek = sestevek_vnosov(vnosi)
    stanje_zaloge = zaloga.dimenzija_tip_zaloga
    data = [{
        "dimenzija": key.split("_")[0],
        "tip": key.split("_")[1],
        "stevilo": sestevek[key]["stevilo"],
        "zaloga": stanje_zaloge[key],
        "razlika": stanje_zaloge[key] - sestevek[key]["stevilo"]
    } for key in sestevek]
    slovar_strank = {
        stranka["id"]: dict(stranka, **{"skupno_stevilo": 0}) for stranka in stranke.values("id","naziv")
    }

    for vnos in vnosi:
        slovar_strank[vnos["baza__stranka"]]["skupno_stevilo"] += vnos["stevilo"] 
    
    keys_to_delete = []
    for key, value in slovar_strank.items():
        if value["skupno_stevilo"] == 0:
            keys_to_delete.append(key)
    for key in keys_to_delete:
        slovar_strank.pop(key)

    return data, slovar_strank.values()

def baza_analize_narocil(request, zaloga):
    pass


def seperate_filter(filter):
    split = filter.split(" ")
    tipi = ["Y","W","JP70"]
    tipi_filter = []
    dimenzija_filter = []
    for filter in split:
        filter = filter.upper()
        if filter in tipi:
            tipi_filter.append(filter)
        else:
            dimenzija_filter.append(filter)
    if len(tipi_filter) == 0:
        tipi_filter = tipi
    return tipi_filter,dimenzija_filter


def sestevek_vnosov_skupno(vnosi):
    slovar = {}
    for dimenzija in Dimenzija.objects.values("dimenzija"):
        for tip in ["Y","W","JP70"]:
            slovar[dimenzija["dimenzija"] + "_" + tip] = 0
    for vnos in vnosi:
        dimenzija_tip = vnos["dimenzija__dimenzija"] + "_" + vnos["tip"]
        slovar[dimenzija_tip] = slovar[dimenzija_tip] + vnos["stevilo"]
    return slovar
    
def join_sestevka(s1, s2, i = 1):
    slovar = s1.copy()
    for vnos in s2:
        slovar[vnos] = slovar[vnos] + s2[vnos] * i
    return slovar

def sestevek_vnosov(vnosi):
    slovar = {}
    for vnos in vnosi:
        dimenzija_tip = vnos["dimenzija__dimenzija"] + "_" + vnos["tip"]
        if dimenzija_tip in slovar:
            slovar[dimenzija_tip]["stevilo"] += vnos["stevilo"]
            slovar[dimenzija_tip]["cena"] += vnos["stevilo"] * vnos["cena"] if vnos["cena"] else 0
        else:
            slovar[dimenzija_tip] = {
                "stevilo": vnos["stevilo"],
                "cena": vnos["cena"] * vnos["stevilo"] if vnos["cena"] else 0
            }
    return slovar
    
def nastavi_cene():
    cene = []
    with open('cene.txt') as dat:
        for vrstica in dat.readlines():
            seznam = vrstica.replace('\n','').split(";")
            slovar = {
                'dimenzija':seznam[0],
                'dnevna_prodaja':{
                        'Y':seznam[1],
                        'W':seznam[2],
                        "JP":seznam[3],
                        "JP50":seznam[4],
                        "JP70":seznam[5]},
                "vele_prodaja":{
                        'Y':seznam[7],
                        'W':seznam[8],
                        "JP":seznam[9],
                        "JP50":seznam[10],
                        "JP70":seznam[11],   
                    }
                }
            cene.append(slovar)
    return cene
    #for x in cene:
    #    for prodaja in ["vele_prodaja","dnevna_prodaja"]:
    #        for tip in ["Y","W","JP","JP50","JP70"]:
    #            cena = Cena.objects.get(sestavina__dimenzija__dimenzija = x["dimenzija"],tip = tip, prodaja = prodaja)
    #            cena.cena = float(x[prodaja][tip])
    #            cena.save()

def ustvari_json_baze(baza):
    if baza.tip == "prevzem":
        slovar = {
            'title':baza.title,
            'datum':str(baza.datum),
            'kontejner':baza.kontejner.stevilka,
            'posiljatelj':baza.kontejner.posiljatelj,
            'drzava':baza.kontejner.drzava,
            'uporabnik':baza.author.username,
            'stevilo':baza.skupno_stevilo,
            'vnosi': []
        }
        for vnos in baza.vnos_set.all():
            slovar['vnosi'].append(
                {
                    'dimenzija': vnos.dimenzija.dimenzija,
                    'stevilo': vnos.stevilo,
                    'tip': vnos.tip
                }
            )
    elif baza.tip == "vele_prodaja":
        slovar = {
            'title':baza.title,
            'datum':str(baza.datum),
            'stranka':baza.stranka.naziv,
            'popust':baza.popust,
            'uporabnik':baza.author.username,
            'stevilo':baza.skupno_stevilo,
            'cena':float(baza.koncna_cena),
            'vnosi': []
        }
        for vnos in baza.vnos_set.all():
            slovar['vnosi'].append(
                {
                    'dimenzija': vnos.dimenzija.dimenzija,
                    'stevilo': vnos.stevilo,
                    'tip': vnos.tip,
                    'cena': flot(vnos.cena),
                }
            )
    elif baza.tip == "racun":
        slovar = {
            'title':baza.title,
            'cas':str(baza.cas),
            'popust':baza.popust,
            'uporabnik':baza.author.username,
            'stevilo':baza.skupno_stevilo,
            'cena':float(baza.koncna_cena),
            'vnosi': []
        }
        for vnos in baza.vnos_set.all():
            slovar['vnosi'].append(
                {
                    'dimenzija': vnos.dimenzija.dimenzija,
                    'stevilo': vnos.stevilo,
                    'tip': vnos.tip,
                    'cena': float(vnos.cena),
                }
            )
    else:
        slovar = {
            'title':baza.title,
            'datum':str(baza.datum),
            'uporabnik':baza.author.username,
            'stevilo':baza.skupno_stevilo,
            'vnosi': []
        }
        for vnos in baza.vnos_set.all():
            slovar['vnosi'].append(
                {
                    'dimenzija': vnos.dimenzija.dimenzija,
                    'stevilo': vnos.stevilo,
                    'tip': vnos.tip,
                }
            )
    with open(baza.title + '.json', 'w') as dat:
        json.dump(slovar, dat, indent=4)

def ustvari_datoteko(baza,ime):
    with open(ime + '.txt', 'w') as dat:
        for vnos in baza.vnos_set.all().order_by('dimenzija'):
            dimenzija = vnos.dimenzija.dimenzija
            dat.write(dimenzija + ';' + vnos.tip + ";" + str(vnos.stevilo) + '\n')
    
def doloci_dimenzijo(radius,height,width,special):
    if special:
        return height + '/' + width + '/' + radius + 'C'
    elif width == "R":
        return height + '/' + radius
    else:
        return height + '/' + width + '/' + radius

def vnosi_iz_datoteke(datoteka,zaloga):
    program = Program.objects.all().first()
    seznam = []
    dimenzije = program.vrni_slovar_dimenzij()
    for vrstica in datoteka.readlines():
        locitev = vrstica.decode().split(";")
        dimenzija = locitev[0]
        tip = locitev[1]
        stevilo = int(locitev[2])
        if dimenzija in dimenzije:
            seznam.append({
                'dimenzija_id':dimenzije[dimenzija],
                'tip':tip,
                'stevilo':stevilo
            })
        else:
            print(dimenzija)
    return seznam

def nova_zaloga(ime,tipi,prodaje):
    tipi = json.dumps(tipi)
    prodaje = json.dumps(prodaje)
    Zaloga.objects.create(title=ime,tipi_sestavine=tipi,tipi_prodaje=prodaje)
    