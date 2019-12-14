from zaloga.models import Sestavina, Baza
from zaloga.models import Zaloga

zaloga = Zaloga.objects.all().first()

class Skripta():
    def __init__(self,narocila):
        self.zaloga = zaloga
        self.narocila = [Narocilo(narocilo) for narocilo in narocila]
        self.skupno = ustvari_skupno(self.narocila,zaloga)
        self.skupno_stevilo = sum([narocilo.skupno_stevilo for narocilo in narocila])
        self.na_zalogi = zaloga.zaloga
        self.na_voljo = zaloga.zaloga

    def razporedi(self,dimenzija,tip):
        # odštej še minimalno zalogo
        skupno = self.skupno[dimenzija][tip]['kolicina']
        zaloga = self.skupno[dimenzija][tip]['zaloga']
        narocila = self.skupno[dimenzija][tip]['narocila']
        if skupno <= zaloga:
        # dodaj maksimum
            for narocilo in narocila:
                narocilo.posiljka[dimenzija][tip] = narocilo.narocilo[dimenzija][tip]
        else:
        #odštej še minimalno
            while skupno > zaloga:
                najmanjsi = min([narocilo.narocilo[dimenzija][tip] for narocilo in narocila])
                for narocilo in narocila:
                    razlika = round(narocilo.narocilo[dimenzija][tip] / najmanjsi)
                    narocilo.narocilo[dimenzija][tip] -= razlika
                    skupno -= razlika
            else:
                while skupno - zaloga < 0:
                    for narocilo in narocila:
                        narocilo.narocilo[dimenzija][tip] += 1
                        skupno += 1
                for narocilo in narocila:
                    narocilo.posiljka[dimenzija][tip] = narocilo.narocilo[dimenzija][tip]

class Narocilo():
    def __init__(self,narocilo):
        self.baza = narocilo
        self.stanka = narocilo.stranka
        self.skupno_stevilo = narocilo.skupno_stevilo
        self.narocilo = vrni_narocilo(narocilo)
        self.posiljka = vrni_posiljko(narocilo)
        
    def izpolnjeno(self):
        for vnos in self.posiljka:
            if vnos.izpoljeno == False:
                return False
        return True

    def ustvari_posiljko(self):
        posiljka = Baza.objects.create(tip='narocilo',title = narocilo.stranka.ime)
        for dimenzija in self.posiljka:
            for tip in self.posiljka[dimenzija]:
                Vnos.objects.create(
                    baza = posiljka,
                    stevilo = self.posiljka[dimenzija][tip],
                    tip = tip,
                    dimenzija__dimenzija = dimenzija,
                    )
        return posiljka
        
def vrni_narocilo(baza):
    narocilo = {}
    vnosi = baza.vnos_set.all().values('stevilo','dimenzija__dimenzija','tip')
    for vnos in vnosi:
        dimenzija = vnos['dimenzija__dimenzija']
        stevilo = vnos['stevilo']
        tip = vnos['tip']
        if dimenzija in narocilo:
            if tip in narocilo[dimenzija]:
                narocilo[dimenzija][tip] += stevilo
            else:
                narocilo[dimenzija][tip] = stevilo
        else:
            narocilo[dimenzija] = {tip:stevilo}
    return narocilo
def vrni_posiljko(baza):
    posiljka = {}
    vnosi = baza.vnos_set.all().values('stevilo','dimenzija__dimenzija','tip')
    for vnos in vnosi:
        dimenzija = vnos['dimenzija__dimenzija']
        stevilo = vnos['stevilo']
        tip = vnos['tip']
        if dimenzija in posiljka:
            posiljka[dimenzija][tip] = 0
        else:
            posiljka[dimenzija] = {tip: 0}
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
        vnosi = narocilo.baza.vnos_set.all().values('stevilo','dimenzija__dimenzija','tip')
        for vnos in vnosi:
            dimenzija = vnos['dimenzija__dimenzija']
            stevilo = vnos['stevilo']
            tip = vnos['tip']
            if dimenzija in skupno:
                if tip in skupno[dimenzija]:
                    skupno[dimenzija][tip]['kolicina'] += stevilo
                    skupno[dimenzija][tip]['ponovitev'] += 1
                    skupno[dimenzija][tip]['narocila'].append(narocilo)
                else:
                    skupno[dimenzija][tip] = {'kolicina':stevilo, 'ponovitev':1,'narocila':[narocilo]}
            else:
                skupno[dimenzija] = {tip:{'kolicina':stevilo,'ponovitev':1,'narocila':[narocilo]}}
    return skupno


