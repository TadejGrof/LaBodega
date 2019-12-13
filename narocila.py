from zaloga.models import Sestavina, Baza

pomembne_dimenzije_l = []
with open('pomembne_dimenzije.txt') as dat:
    for dimenzija in dat.readlines():
        dimenzija = vrstica.replace('\n','')
        pomembne_dimenzije_l.append(dimenzija)

pomembne_dimenzije = Sestavina.objects.filter(dimenzija__dimenzija__in = pomembne_dimenzije_l )

def vrni_mozne_posiljke(narocila,zaloga):
    posiljke = []
    skupno = ustvari_skupno(narocila,zaloga)
    for narocilo in narocila:
        posiljke.append(vrni_posiljko(narocilo,skupno))
    return posiljke

def vrni_posiljko(narocilo,skupno):
    posiljka = Baza.objects.create(tip='narocilo',title = narocilo.stranka.ime)
    for vnos in vnosi:
        stevilo = izracunaj_mozno_kolicino(vnos,skupno)
    
    for vnos in vnosi:
        Vnos.objects.create(
            baza = posiljka,
            stevilo = stevilo,
            tip = vnos.tip
            dimenzija__dimenzija = vnos.dimenzija
            )
    return posiljka

def ustvari_skupno(narocila, zaloga):
    kolicina_zaloge = zaloga.zaloga
    sesteta_narocila = sestej_narocila(narocila)
    for dimenzija in sesteta_narocila:
        tipi = sesteta_narocila[dimenzija]
        for tip in tipi:
            stevilo = tipi[tip]
            tipi[tip].update({'zaloga': kolicina_zaloge[dimenzija][tip]})
    return sesteta_narocila

def sestej_narocila(narocila):
    skupno = {}
    for narocilo in narocila:
        vnosi = narocilo.baza.vnos_set.all().values('stevilo','dimenzija__dimenzija','tip'):
        for vnos in vnosi:
            dimenzija = vnos['dimenzija__dimenzija']
            stevilo = vnos['stevilo']
            if dimenzija in skupno:
                if tip in skupno[dimenzija]:
                    skupno[dimenzija][tip]['kolicina'] += stevilo
                    skupno[dimenzija][tip]['ponovitev'] += 1
                else:
                    skupno[dimenzija][tip] = {'kolicina':stevilo, 'ponovitev':1}
            else:
                skupno[dimenzija] = {tip:{'kolicina:':stevilo,'ponovitev':1}}
    return skupno

def izracunaj_mozno_kolicino(vnos,narocilo,skupno):
    min_zaloge = 0
    dimenzija = vnos.dimenzija
    tip = vnos.tip
    stevila = skupno[dimenzija][tip]
    if dimenzija in minimumi:
        if tip in minimumi[dimenzija]
            min_zaloge = minimumi[dimenzija][tip]
    if stevila[koncno] >= (stevila[zaloga] - min_zaloge):
        return {
            'kolicina': vnos.stevilo
            'maks': maksimum(vnos,narocilo,skupno)
        }
    else:
        kolicina = razporedi(vnos,narocilo,skupno)
        return {
            'kolicina':kolicina,
            'maks':kolicina
        }

def maksimum(vnos,narocilo,skupno):
    stevila = skupno[vnos.dimenzija][vnos.tip]
    zaloga = stevila['zaloga']
    kolicina = stevila['kolicina']
    ponovitev = stevila['ponovitev']
    procent_iz_narocil = vnos.stevilo / kolicina
    procent_iz_sestevka = vnos.stevilo / narocilo.baza.skupno_stevilo
    return vnos.stevilo + ((zaloga - kolicina) // ponovitev)
    
def razporedi(vnos,narocilo,skupno):
    stevila = skupno[vnos.dimenzija][vnos.tip]
    zaloga = stevila['zaloga']
    kolicina = stevila['kolicina']
    ponovitev = stevila['ponovitev']
    procent_narocila = narocila.baza.skupno_stevilo / skupno['skupno']
    procent_iz_narocil = vnos.stevilo / kolicina
    procent_iz_sestevka = vnos.stevilo / narocilo.baza.skupno_stevilo
    razlika = kolicina - zaloga
    if vnos.stevilo < zaloga / ponovitev:
        return vnos.stevilo
    else:
        return int((vnos.stevilo - (razlika * procent_narocila))

