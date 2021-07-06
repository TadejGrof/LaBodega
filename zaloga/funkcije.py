import io
from datetime import datetime
import json 
import os
import shutil
from program.models import Program
from zaloga.models import Zaloga, TIPI_SESTAVINE, Sestavina, Tip, Dimenzija, VnosZaloge, Vnos
import json

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
    
def ustvari_tipe():
    for tip in TIPI_SESTAVINE:
        if not Tip.objects.filter(kratko=tip[0]).exists():
            Tip.objects.create(kratko=tip[0],dolgo=tip[1])

def pretvori_sestavine():
    for sestavina in Sestavina.objects.all().filter(tip=None):
        for tip in TIPI_SESTAVINE:
            vnos_zaloge = VnosZaloge.objects.get(sestavina__tip__kratko=tip[0],zaloga=sestavina.zaloga,sestavina__dimenzija=sestavina.dimenzija)
            vnos_zaloge.stanje = getattr(sestavina,tip[0])
            vnos_zaloge.save()

def pretvori_vnose():
    vnosi = []
    for vnos in Vnos.objects.all():
        try:
            vnos.sestavina = Sestavina.objects.get(dimenzija=vnos.dimenzija, tip=Tip.objects.get(kratko=vnos.tip))
            vnosi.append(vnos)
        except:
            print(vnos.tip)
            if vnos.tip == "70%":
                vnos.sestavina = Sestavina.objects.get(dimenzija=vnos.dimenzija, tip=Tip.objects.get(kratko="JP70"))
                vnosi.append(vnos)
    Vnos.objects.bulk_update(vnosi,["sestavina"])

def pretvorba():
    ustvari_tipe()
    pretvori_sestavine()
    pretvori_vnos()
    
    
