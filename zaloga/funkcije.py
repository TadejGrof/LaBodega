import io
from datetime import datetime
import json 
import os
import shutil

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

def arhiv_baz(baze):
    os.chdir('arhiv')
    for baza in baze:
        os.chdir(baza.tip)
        os.chdir(str(baza.datum.year))
        ustvari_json_baze(baza)
        os.chdir('..')
        os.chdir('..')
    os.chdir('..')

def arhiv_prodaj(prodaje):
    os.chdir('arhiv')
    for prodaja in prodaje:
        os.chdir('dnevna_prodaja')
        os.chdir(str(prodaja.datum.year))
        os.mkdir(prodaja.title)
        os.chdir(prodaja.title)
        for racun in prodaja.baza_set.filter(status='veljavno'):
            ustvari_json_baze(racun)
        os.chdir('..')
        os.chdir('..')
        os.chdir('..')
    os.chdir('..')

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

def ustvari_zacetna_stanja(zaloga,datum):
    stanja = {}
    tipi = zaloga.vrni_tipe
    for sestavina in zaloga.sestavina_set.all():
        slovar = {}
        for tip in tipi:
            stanje = sestavina.zaloga_na_datum(datum,tip[0])
            slovar.update({tip[0]:stanje})
        stanja.update({sestavina.dimenzija.dimenzija:slovar})
    with open('zacetna_stanja.json', 'w') as dat:
        json.dump(stanja, dat, indent=4)

def zacetna_stanja(zaloga):
    stanja = {}
    for sestavina in zaloga.sestavina_set.all().values('dimenzija__dimenzija'):
        slovar = {}
        for tip in zaloga.vrni_tipe:
            slovar.update({tip[0]:0})
        stanja.update({sestavina['dimenzija__dimenzija']:slovar})
    with open('zacetna_stanja.json', 'w') as dat:
        json.dump(stanja, dat, indent=4)

def ustvari_datoteko(baza):
    with open(baza.kontejner.stevilka + '.txt', 'w') as dat:
        for vnos in baza.vnos_set.all().order_by('dimenzija'):
            dimenzija = vnos.dimenzija.dimenzija + '-' + vnos.tip
            dat.write(dimenzija + ';' + str(vnos.stevilo) + '\n')

def sestavine(zaloga):
    with open("sestavine" + '.txt', 'w') as dat:
        for sestavina in zaloga.sestavina_set.all().values("dimenzija__dimenzija"):
            dimenzija = sestavina["dimenzija__dimenzija"]
            dat.write(dimenzija + '\n')
    
def doloci_dimenzijo(radius,height,width,special):
    if special:
        return height + '/' + width + '/' + radius + 'C'
    elif width == "R":
        return height + '/' + radius
    else:
        return height + '/' + width + '/' + radius

def vnosi_iz_datoteke(datoteka,zaloga):
    seznam = []
    dimenzije = zaloga.vrni_slovar_dimenzij()
    for vrstica in datoteka.readlines():
        locitev = vrstica.decode().split(";")
        print(locitev)
        dimenzija = locitev[0]
        tip = locitev[1]
        stevilo = int(locitev[2])
        print(stevilo)
        if dimenzija in dimenzije:
            seznam.append({
                'dimenzija_id':dimenzije[dimenzija],
                'tip':tip,
                'stevilo':stevilo
            })
    return seznam

def dodaj_sestavine_iz_datoteke(datoteka):
    seznam = []
    for vrstica in datoteka.readlines():
        locitev = vrstica.decode().split(";")
        radius = 'R' + locitev[0]
        height = locitev[1]
        width = locitev[2]
        special = False
        if locitev[3].replace('\n','').strip() == "TRUE":
            special = True
        dimenzija = doloci_dimenzijo(radius,height,width,special)
        seznam.append({
            'dimenzija': dimenzija,
            'radius': radius,
            'height': height,
            'width': width,
            'special': special,
        })
    return seznam


def ponastavi_program(program,zaloga=True,baze=True,stranke=False,cene=False,datoteke=True):
    if zaloga:
        program.ponastavi_zalogo()
        zacetna_stanja(program)
    if baze:
        program.baza_set.all().delete()
        program.dnevna_prodaja_set.all().delete()
    if cene:
        program.ponastavi_cene()
    if stranke:
        program.ponastavi_stranke()
    if datoteke:
        for tip in ['prevzem','odpis','vele_prodaja','dnevna_prodaja']:
            for leto in ['2019','2020']:
                for root, dirs, files in os.walk(os.path.join(os.getcwd(),'arhiv',tip,leto)):
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d))
                

