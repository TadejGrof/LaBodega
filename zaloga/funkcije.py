import io
import datetime
import json 
import os
import shutil
from program.models import Program
from zaloga.models import Baza,Kontejner,Stranka,Zaloga, TIPI_SESTAVINE, Sestavina, Tip, Dimenzija, VnosZaloge, Vnos, Cena
import json
from django.contrib.auth.models import User

def baze_from_json(baze_json):
    if isinstance(baze_json,str):
        baze_json = json.loads(baze_json)
    for baza_json in baze_json:
        baza_from_json(baza_json)

def dnevne_prodaje_from_json(prodaje_json):
    if isinstance(prodaje_json,str):
        prodaje_json = json.loads(prodaje_json)
    for prodaja_json in prodaje_json:
        dnevna_prodaja_from_json(prodaja_json)

def exists_baza_from_json(baza_json):
    return Baza.objects.filter(title = baza_json['title']).exists()

def baza_from_json(baza_json):
    if isinstance(baza_json,str):
        baza_json = json.loads(baza_json)
    if exists_baza_from_json(baza_json):
        baza = Baza.objects.get(title=baza_json["title"])
        baza.vnos_set.all().delete()
    else:
        baza = Baza.objects.create()
    baza.author = User.objects.all().get(id=baza_json['author'])
    baza.popust = baza_json['popust']
    baza.prevoz = baza_json['prevoz']
    baza.kontejner = kontejner_from_json(baza_json['kontejner']) if baza_json['kontejner'] != None else None
    baza.stranka = Stranka.objects.get(id=baza_json['stranka']) if baza_json['stranka'] != None else None
    baza.sprememba_zaloge = baza_json['sprememba_zaloge']
    baza.tip = baza_json['tip']
    baza.title = baza_json['title']
    baza.zaloga = Zaloga.objects.get(id=baza_json['zaloga'])
    baza.zalogaPrenosa = baza_json['zaloga_prenosa']
    baza.status = baza_json['status']
    baza.datum = datetime.datetime.strptime(baza_json['datum'],'%Y-%m-%d')
    baza.placilo = baza_json['placilo']
    baza.save()
    for vnos in baza_json['vnosi']:
        sestavina = Sestavina.objects.get(dimenzija_id=vnos['dimenzija'], tip__kratko=vnos['tip'])
        stevilo = vnos['stevilo']
        cena = vnos['cena']
        baza.dodaj_vnos(sestavina,stevilo,cena)
    return baza

def kontejner_from_json(kontejner_json):
    return Kontejner.objects.create(
        stevilka = kontejner_json["stevilka"],
        drzava = kontejner_json["drzava"],
        posiljatelj = kontejner_json["posiljatelj"]
    )
    
def dnevna_prodaja_from_json(prodaja_json):
    if isinstance(prodaja_json,str):
        prodaja_json = json.loads(prodaja_json)
    datum = datetime.datetime.strptime(baza_json['datum'],'%Y-%m-%d')
    prodaja = Dnevna_prodaja.objects.all().filter(datum=datum).first()
    if prodaja == None:
        prodaja = Dnevna_prodaja.objects.create(
            datum = datetime.datetime.strptime(baza_json['datum'],'%Y-%m-%d')
        )
    prodaja.baza_set.all().delete()
    for racun_json in prodaja_json["racuni"]:
        baza = baza_from_json(racun_json)
        baza.dnevna_prodaja = prodaja
        baza.save()

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

def pretvori_cene():
    z1 = Zaloga.objects.first()
    z2 = Zaloga.objects.all()[1]
    
    for sestavina in Sestavina.objects.all().exclude(tip=None):
        cena = Cena.objects.create(prodaja="vele_prodaja",sestavina=sestavina)
        cene = Cena.objects.all().filter(prodaja="vele_prodaja",sestavina__tip=None,sestavina__dimenzija = sestavina.dimenzija,tip=sestavina.tip.kratko).exclude(cena=0)
        if len(cene) > 0:
            cena.cena = cene.first().cena
            cena.save()
        z1.cenik.add(cena)
        cena = Cena.objects.create(prodaja="dnevna_prodaja",sestavina=sestavina)
        cene = Cena.objects.all().filter(prodaja="dnevna_prodaja",sestavina__tip=None,sestavina__dimenzija = sestavina.dimenzija,tip=sestavina.tip.kratko).exclude(cena=0)
        if len(cene) > 0:
            cena.cena = cene.first().cena
            cena.save()
        z2.cenik.add(cena)

    
    
