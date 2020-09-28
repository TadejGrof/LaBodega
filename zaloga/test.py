from .models import Dnevna_prodaja, Zaloga, Sestavina, Baza, Sprememba

dnevne_prodaje = Dnevna_prodaja.objects.all()[::-1]

def test_dnevna_prodaja(odDatum,doDatum):
    prodaje = dnevne_prodaje.filter(datum__lte = doDatum, datum__gte = odDatum)
    test_prodaje(prodaje)

def test_prodaje(prodaje):
    for prodaja in prodaje:
        print("delam " + str(prodaja.datum) + ":")
        for racun in prodaja.baza_set.all().filter(status="veljavno"):
            napacno = False
            for vnos in racun.vnos_set.all():
                if vnos.sprememba == None:
                   napacno = True
            if napacno:
                print("popravljam racun " + str(racun))
                cas = racun.cas
                racun.uveljavi_racun(racun.zaloga)
                racun.cas = cas
                racun.save()
        print("konec")

def popravi_racune(prodaje):
    for prodaja in prodaje:
        print("delam " + str(prodaja.datum) + ":")
        for racun in prodaja.baza_set.all().filter(status="veljavno"):
            racun.datum = prodaja.datum
            racun.save()
            for vnos in racun.vnos_set.all():
                vnos.save()
