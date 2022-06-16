import io
from datetime import datetime
import json
from msilib.schema import Error 
import os
import shutil
from program.models import Program
from zaloga.models import Zaloga, Dimenzija
import json
from django.db.models import F

import random

def random_color():
    r = random.randint(0,255)
    g = random.randint(0,255)
    b = random.randint(0,255)
    return [r,g,b]

def filtriraj_dimenzije(filter):
    if isinstance(filter, str):
        split = filter.split(" ")
    elif isinstance(filter, list):
        split = filter
    else:
        raise Error("NEPRAVILNA OBLIKA FILTRA")
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
    