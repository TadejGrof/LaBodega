from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import datetime
import os
from django.contrib.auth.models import User
from prodaja.models import Prodaja, Stranka, Naslov
import json
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now

TIPI_SESTAVINE = (
        ('Y','Yellow'),
        ('W','White'),
        ('JP', 'Japan'),
        ('JP50', 'Japan50%'),
        ('JP70', 'Japan70%'),
    )

TIPI_PRODAJE = (
        ('dnevna_prodaja', 'Dnevna_prodaja'),
        ('vele_prodaja', 'Vele_prodaja')
    )

TIPI_CEN = (
        ('prodaja', 'Prodaja'),
        ('nakup', 'Nakup')
    )


POSILJATELJI = (
    ('bozo', 'Bozo'),
    ('japan', 'Japan'),
)

DRZAVE = (
    ('slo', 'Slovenia'),
    ('jap', 'Japan'),
    ('pol', 'Poland'),
    ('ang', 'England'),
    ('kor', 'Korea'),
    ('pan', 'Panama'),
)

TIPI_BAZE = (
    ('inventura', 'Inventura'),
    ('prevzem','Prevzem'),
    ('odpis', 'Odpis'),
    ('vele_prodaja', 'Vele prodaja'),
    ('racun','Racun'),
    ('narocilo','Narocilo'),
    ('prenos', 'Prenos med skladišči'),
)

TIPI_STROSKOV = (
    ('placilo','Placilo'),
    ('kontejner','Kontejner'),
    ('najem', 'Najemnina'),
    ('placa','Placa'),
    ('drugo','Drugo')
)


class Zaloga(models.Model):
    title = models.CharField(default="skladisce", max_length=20)
    tipi_prodaje = models.CharField(default='["vele_prodaja"]', max_length=50)
    tipi_sestavine = models.CharField(default='["Y","W","JP","JP50","JP70"]', max_length=50)

    def __str__(self):
        return self.title

    @property
    def tipi_prodaj(self):
        return json.loads(self.tipi_prodaje)

    @property
    def tipi_sestavin(self):
        return json.loads(self.tipi_sestavine)
           
    @property
    def danes(self):
        return datetime.today().strftime('%Y-%m-%d')

    @property
    def dimenzija_tip_zaloga(self):
        zaloga = self.zaloga
        dimenzija_tip = {}
        for dimenzija in zaloga:
            for tip in zaloga[dimenzija]:
                dimenzija_tip.update({dimenzija + '_' + tip : zaloga[dimenzija][tip]})
        return dimenzija_tip

    @property
    def zaloga(self):
        dimenzije = self.vrni_slovar_dimenzij(True)
        zaloga = {}
        for sestavina in self.sestavina_set.all().values():
            dimenzija = dimenzije[sestavina['dimenzija_id']]
            zaloga.update({dimenzija:{}})
            for tip in self.tipi_sestavin:
                zaloga[dimenzija].update({tip:sestavina[tip]})
        return zaloga

    @property            
    def rezervirane(self):
        rezervirane = {}
        for baza in self.baza_set.all().filter(status="aktivno", tip="vele_prodaja"):
            for vnos in baza.vnos_set.all().values('dimenzija__dimenzija','stevilo','tip'):
                dimenzija = vnos['dimenzija__dimenzija']
                stevilo = vnos['stevilo']
                tip = vnos['tip']
                dimenzija_tip = dimenzija + '_' + tip
                if dimenzija_tip in rezervirane:
                    rezervirane[dimenzija_tip] += stevilo
                else:
                    rezervirane[dimenzija_tip] = stevilo
        return rezervirane

    @property
    def na_voljo(self):
        zaloga = self.dimenzija_tip_zaloga
        rezervirane = self.rezervirane
        for sestavina in rezervirane:
            zaloga[sestavina] -= rezervirane[sestavina]
        return zaloga

    @property
    def vrni_razlicne_radiuse(self):
        razlicni_radiusi = []
        for radius in self.sestavina_set.all().values('dimenzija__radius').distinct().order_by('dimenzija__radius'):
                razlicni_radiusi.append(radius['dimenzija__radius'])
        return razlicni_radiusi

    def ponastavi_zalogo(self):
        for sestavina in self.sestavina_set.all():
            for tip in self.vrni_tipe:
                setattr(sestavina,tip[0],0)
            sestavina.save()

    def cenik(self,tip='vele_prodaja'):
        cene = {}
        cenik = self.sestavina_set.all().prefetch_related('cena_set').filter(cena__prodaja=tip).values(
            'dimenzija__dimenzija',
            'pk',
            'cena',
            'cena__tip',
            'cena__cena')
        for cena in cenik:
            dimenzija = cena['dimenzija__dimenzija']
            tip = cena['cena__tip']
            cena = cena['cena__cena']
            if dimenzija in cene:
                if not tip in cene[dimenzija]:
                    cene[dimenzija].update({tip:float(cena)})
            else:
                    cene.update({dimenzija:{tip:float(cena)}})
        return cene

    def vrni_slovar_dimenzij(self, obratno = False):
        slovar = {}
        dimenzije = self.sestavina_set.values('dimenzija_id','dimenzija__dimenzija')
        if obratno:
            for dimenzija in dimenzije:
                slovar.update({dimenzija['dimenzija_id']:dimenzija['dimenzija__dimenzija']})
        else: 
            for dimenzija in dimenzije:
                slovar.update({dimenzija['dimenzija__dimenzija']:dimenzija['dimenzija_id']})
        return slovar

    def vrni_top_10(self,radius="all"):
        sestavine = []
        radiusi = self.vrni_razlicne_radiuse
        tipi = self.vrni_tipe
        if radius in radiusi:
            sestavine_radiusa = self.sestavina_set.all().filter(dimenzija__radius = radius)
            for tip in tipi:
                for sestavina in sestavine_radiusa.order_by('-' + tip[0])[:10].values(tip[0],'dimenzija__dimenzija'):
                    sestavine.append((sestavina[tip[0]],tip[0],sestavina['dimenzija__dimenzija']))
            sestavine.sort()
            sestavine = sestavine[::-1][:10]
        else:
            for radius in radiusi:
                sestavine_radiusa = self.sestavina_set.all().filter(dimenzija__radius = radius)
                for tip in tipi:
                    for sestavina in sestavine_radiusa.order_by('-' + tip[0])[:10].values(tip[0],'dimenzija__dimenzija'):
                        sestavine.append((sestavina[tip[0]],tip[0],sestavina['dimenzija__dimenzija']))
            sestavine.sort()
            sestavine = sestavine[::-1][:10]
        return [{'dimenzija__dimenzija':sestavina[2],sestavina[1]:sestavina[0],'tip':sestavina[1]} for sestavina in sestavine]
    
    @property
    def vrni_tipe(self):
        return TIPI_SESTAVINE

    @property
    def tipi_stroskov(self):
        return TIPI_STROSKOV

    @property
    def drzave(self):
        return DRZAVE
    
    @property
    def posiljatelji(self):
        return POSILJATELJI

    def vrni_dimenzijo(self,radius,height,width):
        special = False
        if "C" in width:
            special = True
            width = width[:-1]
        return Dimenzija.objects.get(radius = radius,height=height,width=width,special=special)
 
    @property
    def vrni_zalogo(self):
        sestavine = self.sestavina_set.all().values()
        dimenzije = Dimenzija.objects.all().values()
        for sestavina in sestavine:
            for dimenzija in dimenzije:
                if dimenzija['id'] == sestavina['dimenzija_id']:
                    sestavina.update({'dimenzija':dimenzija['dimenzija'],'radius':dimenzija['radius']})
        return sestavine

    @property
    def vrni_sestavine(self):
        return self.sestavina_set.all()

    @property
    def zaklep_zaloge(self):
        return self.zaklep_set.all().first()

    @property
    def datum_zaklepa(self):
        return self.zaklep_zaloge.datum

    def zakleni_zalogo(self,datum):
        if datum > self.datum_zaklepa:
            zaklep_json = {}
            for sestavina in self.sestavina_set().all():
                pk = sestavina.pk
                zaklep_json[pk] = {}
                for tip in self.tipi_sestavin:
                    tip = tip[0]
                    zaklep_json[pk][tip] = sestavina.getattr(tip)
            Zaklep.objects.create(zaloga = self, datum = datum,stanja = json.dumps(zaklep_json))
        else:
            print("IZBERI DATUM PO PREJŠNJEM ZAKLEPU")

class Zaklep(models.Model):
    zaloga = models.ForeignKey(Zaloga,default=1,on_delete=models.CASCADE)
    datum = models.DateField(default=now)
    stanja_json = models.TextField(default="{}")

    class Meta:
        ordering = ['-datum']

    @property
    def stanja(self):
        return json.loads(self.stanja_json)

    def vrni_stanje(self,sestavina,tip):
        stanja = self.stanja
        return stanja[str(sestavina.pk)][tip]


class Zaposleni(models.Model):
    user = models.OneToOneField(User,default=None,blank=True,null=True,on_delete=models.CASCADE)
    zaloga = models.ForeignKey(Zaloga,default=1,on_delete=models.CASCADE)
    ime = models.CharField(default="/",max_length=20)
    priimek = models.CharField(default="/",max_length=20)
    davcna = models.CharField(default="/", max_length=30)
    naslov = models.OneToOneField(Naslov, default=None, on_delete=models.CASCADE, null=True, blank=True)
    telefon = models.CharField(default="/", max_length=20)
    mail = models.CharField(default="/", max_length=40)

class Dimenzija(models.Model):
    dimenzija = models.CharField(default="", max_length=20)
    radius = models.CharField(max_length=10)
    height = models.CharField(max_length=10)
    width = models.CharField(max_length=10)
    special = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['radius', 'height', 'width' , 'special']

    def __str__(self):
        return self.dimenzija

##################################################################################################
class Sestavina(models.Model):
    zaloga = models.ForeignKey(Zaloga,default=1, on_delete=models.CASCADE)
    dimenzija = models.ForeignKey(Dimenzija, on_delete=models.CASCADE)
    Y = models.IntegerField(default = 0)
    W = models.IntegerField(default = 0)  
    JP = models.IntegerField(default = 0)
    JP50 = models.IntegerField(default = 0)
    JP70 = models.IntegerField(default = 0)

    class Meta:
        ordering = ['zaloga','dimenzija']

    def cena(self,prodaja,tip):
        if prodaja == "vele_prodaja" or prodaja == "dnevna_prodaja":
            return self.cena_set.all().get(tip=tip, prodaja = prodaja).cena
        else:
            return None

    def nastavi_novo_ceno(self, prodaja, tip, nova_cena):
        cena = self.cena_set.all().get(tip=tip,prodaja=prodaja)
        cena.cena = nova_cena
        cena.save()
        
    def spremeni_stevilo(self,stevilo,tip):
        for tip_zaloge in self.zaloga.vrni_tipe:
            if tip_zaloge[0] == tip:
                stevilo = getattr(self,tip_zaloge[0]) + stevilo
                setattr(self,tip,stevilo)
        self.save()

    def prodaja(self,tip_baze,tip,zacetek,konec):
        spremembe = self.sprememba_set.all().filter(baza__tip = tip_baze, tip=tip, baza__datum__gte = zacetek, baza__datum__lte = konec)
        cena = 0
        stevilo = 0
        for sprememba in spremembe:
            popust = 0
            if tip_baze == "vele_prodaja":
                popust = sprememba.baza.popust
            for vnos in sprememba.vnos_set.all().values('stevilo','cena'):
                stevilo += vnos['stevilo']
                cena += round(float(vnos['stevilo'] * float(vnos['cena']) * ((100 - popust) / 100)))
        return stevilo, cena

    def __str__(self):
        return self.dimenzija.dimenzija

    @property
    def prijazna_dimenzija(self):
        return self.dimenzija.dimenzija.replace('/','-')

    def nastavi_iz_sprememb(self,tip):
        zaklep = self.zaloga.zaklep_zaloge
        datum = zaklep.datum
        stanje = zaklep.vrni_stanje(self,tip)
        spremembe = self.sprememba_set.all().filter(tip = tip,baza__datum__gt = datum).order_by('baza__datum','baza__cas')
        for sprememba in spremembe:
            if sprememba.stanje == None:
                stanje += sprememba.stevilo * sprememba.baza.sprememba_zaloge
            else:
                stanje = sprememba.stanje
        setattr(self,tip,stanje)
        self.save()

    def zaloga_na_datum(self,datum,tip):
        datum = datum.split("-")
        datum = datetime(int(datum[0]),int(datum[1]),int(datum[2])).date()
        spremembe = self.sprememba_set.all().filter(tip = tip)
        zaloga = self.zaloga
        zaklep = zaloga.zaklep_zaloge
        stanje = zaloga.zaklep_zaloge.vrni_stanje(self,tip)

        if zaklep.datum < datum:
            spremembe = spremembe.filter(baza__datum__gt = zaklep.datum, baza__datum__lte = datum).order_by('baza__datum','baza__cas')
            for sprememba in spremembe:
                if sprememba.stanje == None:
                    stanje += sprememba.stevilo * sprememba.baza.sprememba_zaloge
                else:
                    stanje = sprememba.stanje
        # gledamo od zaklepa navzdol:
        elif zaklep.datum > datum:
            spremembe = spremembe.filter(baza__datum__lte = zaklep.datum, baza__datum__gte = datum).order_by('-baza__datum','-baza__cas')
            for sprememba in spremembe:
                if sprememba.stanje == None:
                    stanje -= sprememba.stevilo * sprememba.baza.sprememba_zaloge
                else:
                    stanje = sprememba.stanje
        print(stanje)
        return stanje

    def vrni_stanja(self,tip,odDatum,doDatum):
        spremembe = self.sprememba_set.all().filter(tip=tip,baza__datum__gt=odDatum, baza__datum__lte=doDatum).order_by('baza__datum','baza__cas')
        stanje = self.zaloga_na_datum(odDatum,tip)
        zaporedna_stanja = [stanje]
        for sprememba in spremembe.values('baza__sprememba_zaloge','stanje','stevilo','pk'):
            if sprememba['stanje'] == None:
                stanje += sprememba['stevilo'] * sprememba['baza__sprememba_zaloge']
                zaporedna_stanja.append(stanje)
            else:
                razlika = sprememba['stanje'] - stanje
                stanje = sprememba['stanje']
                sprememba = Sprememba.objects.get(pk=sprememba['pk'])
                sprememba.stevilo = razlika
                sprememba.save()
                zaporedna_stanja.append(stanje)
        return zaporedna_stanja

@receiver(post_save, sender=Zaloga)
def create_zaloga(sender, instance, created, **kwargs):
    if created:
        for dimenzija in Dimenzija.objects.all():
            Sestavina.objects.create(zaloga=instance,dimenzija=dimenzija)

@receiver(post_save, sender=Dimenzija)
def create_dimenzija(sender, instance, created, **kwargs):
    if created:
        for zaloga in Zaloga.objects.all():
            sestavina = Sestavina.objects.create(zaloga = zaloga, dimenzija = instance)

@receiver(post_save, sender=Sestavina)
def create_sestavina(sender, instance, created, **kwargs):
    if created:
        zaloga = instance.zaloga
        for prodaja in zaloga.tipi_prodaj:
            for tip in zaloga.tipi_sestavin:
                Cena.objects.create(sestavina = instance, prodaja = prodaja, tip = tip, nacin="prodaja")

###################################################################################################

class Cena(models.Model):
    sestavina = models.ForeignKey(Sestavina, default=0, on_delete=models.CASCADE)
    cena = models.DecimalField(decimal_places=2,max_digits=5,default=0)
    nacin = models.CharField(max_length=10, choices=TIPI_CEN, default="prodaja")
    tip = models.CharField(max_length=4, choices=TIPI_SESTAVINE, default="Y")
    prodaja = models.CharField(max_length=15, choices=TIPI_PRODAJE, null=True, blank=True, default=None)
    drzava = models.CharField(max_length=15, choices=DRZAVE, null=True,blank=True,default=None)
    
class Kontejner(models.Model):
    stevilka = models.CharField(default="", max_length=20)
    posiljatelj = models.CharField(default="", max_length=20, choices=POSILJATELJI)
    drzava = models.CharField(default="", max_length=20, choices=DRZAVE)

##################################################################################################

class Dnevna_prodaja(models.Model):
    zaloga = models.ForeignKey(Zaloga, default=1, on_delete=models.CASCADE)
    prodaja = models.ForeignKey(Prodaja, default=1, on_delete=models.CASCADE)
    datum = models.DateField(default=timezone.now)
    title = models.CharField(default="", max_length=20)
    tip = 'dnevna_prodaja'

    @property
    def stevilo_racunov(self):
        return self.racun_set.all().count()

    @property
    def stevilo_veljavnih_racunov(self):
        return self.racun_set.all().filter(status='veljavno').count()

    @property
    def aktivni_racun(self):
        return self.baza_set.all().filter(tip='racun', status = "aktivno").first()

    def doloci_title(self):
        dan = str(self.datum.day)
        if len(dan) == 1:
            dan = "0" + dan
        mesec = str(self.datum.month)
        if len(mesec) == 1:
            mesec = "0" + mesec
        leto = str(self.datum.year)
        self.title = dan + '-' + mesec + '-' + leto
        self.save()

    def __str__(self):
        return self.title

    @property
    def racuni(self):
        return self.baza_set.filter(tip='racun',status='veljavno').order_by('-pk').prefetch_related('vnos_set')

    def stevilo_veljavnih_racunov(self):
        return self.baza_set.filter(tip="racun",status="veljavno").count()
    
    @property
    def urejeni_vnosi(self):
        return Vnos.objects.filter(baza__dnevna_prodaja = self, baza__status="veljavno").order_by('dimenzija')

    @property 
    def skupna_cena(self):
        cena = 0
        for vnos in Vnos.objects.filter(baza__dnevna_prodaja=self,baza__status="veljavno"):
            cena += vnos.cena * vnos.stevilo
        return cena

    @property 
    def skupno_stevilo(self):
        stevilo = 0
        for vnos in Vnos.objects.filter(baza__dnevna_prodaja=self,baza__status="veljavno"):
            stevilo += vnos.stevilo
        return stevilo
        
    @property
    def prodane(self):
        prodane = {}
        for vnos in self.urejeni_vnosi:
            dimenzija_vnos = str(vnos.dimenzija) + '-' + vnos.tip
            if dimenzija_vnos in prodane:
                prodane[dimenzija_vnos]['stevilo'] += vnos.stevilo
                prodane[dimenzija_vnos]['cena'] += vnos.cena * vnos.stevilo
            else:
                slovar = {'dimenzija':vnos.dimenzija.dimenzija, 'stevilo':vnos.stevilo,'tip':vnos.tip,'cena':vnos.cena * vnos.stevilo}
                prodane.update({dimenzija_vnos:slovar})
        return prodane

    @property
    def activity_log(self):
        activity_log = []
        for racun in self.racuni:
            for vnos in racun.vnos_set.all():
                activity_log.append({
                    'dimenzija':vnos.dimenzija,
                    'stevilo':vnos.stevilo,
                    'tip':vnos.tip,
                    'cena':vnos.stevilo * vnos.cena,
                    'cas': racun.cas,
                })
        return activity_log

class Baza(models.Model):
    author = models.ForeignKey(User,default=1, on_delete=models.CASCADE)
    title = models.CharField(default="",max_length=15)
    datum = models.DateField(default=timezone.now)
    zaloga = models.ForeignKey(Zaloga, default=1 ,on_delete=models.CASCADE)
    status = models.CharField(default="aktivno",max_length=10)
    sprememba_zaloge = models.IntegerField(default = -1)
    tip = models.CharField(default="prevzem",max_length=20, choices=TIPI_BAZE)
    kontejner = models.OneToOneField(Kontejner,null=True,default=None,blank=True, on_delete=models.CASCADE)
    popust = models.IntegerField(default = None, null=True, blank=True)
    stranka = models.ForeignKey(Stranka, on_delete=models.CASCADE, default=None, null=True, blank=True)
    cas = models.TimeField(default=None,null=True,blank=True)
    dnevna_prodaja = models.ForeignKey(Dnevna_prodaja, on_delete=models.CASCADE, default=None, null=True, blank=True)
    prevoz = models.DecimalField(default=None,null=True,blank=True,max_digits=5, decimal_places=2)

    def __str__(self):
        return self.title
    
    #def save(self, *args, **kwargs):
    #    baza = Baza.objects.get(pk = self.pk)
    #    print(baza.prevoz)
    #    print(self.prevoz)
    #    super(Baza, self).save(*args, **kwargs)

    def skupnoStevilo(self,tip):
        skupno = 0
        for vnos in self.vnosi_values:
            if vnos["tip"] == tip:
                skupno += vnos["stevilo"]
        return skupno

    def skupnaCena(self,tip):
        skupno = 0
        for vnos in self.vnosi_values:
            if vnos["tip"] == tip:
                skupno += vnos["cena"] * vnos["stevilo"]
        return skupno

    def uveljavi_inventuro(self,zaloga, datum = None, cas = None):
        self.status = "veljavno"
        self.doloci_cas(cas)
        self.doloci_datum(datum)
        spremembe = []
        for vnos in self.vnos_set.all().values():
            sestavina = Sestavina.objects.get(zaloga = zaloga, dimenzija_id = vnos['dimenzija_id'])
            tip = vnos["tip"]
            stevilo = vnos["stevilo"]
            setattr(sestavina,tip,stevilo)
            sestavina.save()
            spremembe.append(
                Sprememba(
                baza=self,
                sestavina=sestavina,
                tip=tip,
                stanje=stevilo,
                )
            )
        Sprememba.objects.bulk_create(spremembe)

    def uveljavi_racun(self,zaloga, cas = None):
        self.status = "veljavno"
        self.doloci_cas(cas)
        for vnos in self.vnos_set.all():
            sestavina = Sestavina.objects.get(zaloga = zaloga, dimenzija = vnos.dimenzija)
            sprememba = Sprememba.objects.filter(baza__dnevna_prodaja = self.dnevna_prodaja, sestavina = sestavina, tip = vnos.tip ).first()
        if sprememba == None:
                sprememba = Sprememba.objects.create(
                    sestavina = sestavina,
                    tip = vnos.tip,
                    stevilo = vnos.stevilo,
                    baza = self)
        vnos.sprememba = sprememba
        vnos.save()
        self.save()

    def uveljavi(self,zaloga,datum=None,cas = None):
        self.status = "veljavno"
        self.doloci_cas(cas)
        self.doloci_datum(datum)
        for vnos in self.vnos_set.all():
            sestavina = Sestavina.objects.get(zaloga = zaloga, dimenzija = vnos.dimenzija)
            tip = vnos.tip
            sestavina.spremeni_stevilo(self.sprememba_zaloge * vnos.stevilo, vnos.tip)
            sprememba = Sprememba.objects.filter(baza = self, sestavina = sestavina, tip = vnos.tip ).first()
            if sprememba:
                sprememba.stevilo += vnos.stevilo
                sprememba.save()
            else:
                sprememba = Sprememba.objects.create(
                    sestavina = sestavina,
                    tip = vnos.tip,
                    stevilo = vnos.stevilo,
                    baza = self)
            vnos.sprememba = sprememba
            vnos.save()

    def razveljavi(self):
        if self.status == "veljavno":
            self.status = "aktivno"
            for vnos in self.vnos_set.all():
                sestavina = vnos.sprememba.sestavina
                sprememba = vnos.sprememba
                vnos.sprememba = None
                vnos.save()
                sprememba.delete()
                sestavina.nastavi_iz_sprememb(vnos.tip)
        self.save()

    def razlicni_tipi(self):
        tipi = []
        for vnos in self.vnos_set.all().values('tip'):
            if not vnos['tip'] in tipi:
                tipi.append(vnos['tip'])
        return tipi

    def dodaj_vnos(self,dimenzija,tip,stevilo):
        vnos = Vnos.objects.create(dimenzija=dimenzija,tip=tip,stevilo=stevilo,baza=self)
        if self.status == 'veljavno':
            sestavina = Sestavina.objects.get(dimenzija__dimenzija = dimenzija)
            sprememba = Sprememba.objects.filter(baza=self, sestavina = sestavina, tip=tip).first()
            if sprememba == None:
                sprememba = Sprememba.objects.create(
                    baza=self,
                    sestavina=sestavina,
                    tip=tip,
                    stevilo=stevilo,
                    )
            else:
                sprememba.dodaj_stevilo(vnos.stevilo)
            sestavina.nastavi_iz_sprememb(tip)

    def doloci_cas(self,cas):
        if cas == None:
            self.cas = timezone.localtime(timezone.now())
        else:
            self.cas = cas
        self.save()

    def doloci_datum(self,datum):
        if datum == None:
            self.datum = timezone.localtime(timezone.now())
        else:
            self.datum = datum
        self.save()

    @property
    def vrni_vnose(self):
        return self.vnos_set.all()

    @property
    def vnosi_values(self):
        return self.vnos_set.all().order_by('dimenzija').values(
            'dimenzija__dimenzija',
            'dimenzija__radius',
            'pk',
            'stevilo',
            'tip',
            'cena',
        )
    @property
    
    def stevilo_vnosov(self):
        return self.vnos_set.all().count()

    @property
    def uveljavljeni_vnosi(self):
        vnosi = {}
        for vnos in self.vnosi_values:
            dimenzija_tip = vnos['dimenzija__dimenzija'] + '_' + vnos['tip']
            if not dimenzija_tip in vnosi:
                slovar = {
                    'stevilo': vnos['stevilo'],
                    'tip': vnos['tip'],
                    'dimenzija': vnos['dimenzija__dimenzija'],
                    'pk': vnos['pk']
                }
                vnosi.update({dimenzija_tip: slovar})
        return vnosi

    @property 
    def dimenzija_tip_vnosi(self):
        vnosi = {}
        for vnos in self.vnosi_values:
            dimenzija_tip = vnos['dimenzija__dimenzija'] + '_' + vnos['tip']
            if not dimenzija_tip in vnosi:
                vnosi.update({dimenzija_tip: vnos['stevilo']})
            else:
                vnosi[dimenzija_tip] += vnos['stevilo']
        return vnosi

    @property
    def inventurni_vnosi(self):
        vnosi = {}
        count = 0
        for sestavina in self.zaloga.vrni_zalogo:
            for tip in self.zaloga.vrni_tipe:
                count += 1
                slovar = {'dimenzija': sestavina['dimenzija'],
                        'tip': tip[0],
                        'zaloga': sestavina[tip[0]],
                        'radius': sestavina['radius'],
                        'pk': count,
                        'vneseno':False,
                        'pk_vnosa':None,
                        'stevilo':None
                }
                vnosi.update({sestavina['dimenzija'] + '_' + tip[0]: slovar})
        for vnos in self.vnos_set.all().values('dimenzija__dimenzija','pk','stevilo','tip'):
            slovar['vneseno'] = True
            slovar['pk_vnosa'] = vnos['pk']
            slovar['stevilo'] = vnos['stevilo']
        return vnosi

    @property
    def skupno_stevilo(self):
        stevilo = 0
        for vnos in self.vnos_set.all():
            stevilo += vnos.stevilo
        return stevilo

    @property
    def skupna_cena(self):
        try:
            cena = 0
            for vnos in self.vnos_set.all():
                cena += vnos.skupna_cena
            return cena
        except:
            return None

    @property
    def cena_popusta(self):
        try:
            return round(float(self.skupna_cena) * (self.popust / 100))
        except:
            return None

    @property
    def cena_prevoza(self):
        if self.prevoz != None:
            return round(float(self.skupno_stevilo * self.prevoz))
    
    @property
    def koncna_cena(self):
        try:
            if self.prevoz != None:
                return self.skupna_cena - self.cena_popusta + self.cena_prevoza
            else:
                return self.skupna_cena - self.cena_popusta
        except:
            return None
###################################################################################################

class Sprememba(models.Model):
    zaloga = models.ForeignKey(Zaloga, default=1, on_delete=models.CASCADE)
    sestavina = models.ForeignKey(Sestavina, default=1, on_delete=models.CASCADE)
    stanje = models.IntegerField(default=None,null=True,blank=True)
    baza = models.ForeignKey(Baza,default=0,on_delete=models.CASCADE)
    stevilo = models.IntegerField(default=0)
    tip = models.CharField(default="",choices=TIPI_SESTAVINE, max_length=10)

    def __str__(self):
        return self.baza.tip  + '/' + str(self.stevilo) + '/' + self.tip
    
    def doloci_datum(self):
        self.datum_spremembe = self.baza.datum
        self.save()

    def nastavi_iz_vnosov(self):
        stevilo = 0
        if self.baza.tip == "inventura":
            stevilo = self.vnos_set.all().first().stevilo
            if not self.stanje == stevilo:
                self.stanje = stevilo
                self.save()
        else:
            for vnos in self.vnos_set.all().values('stevilo'):
                stevilo += vnos['stevilo']
            if not self.stevilo == stevilo:
                self.stevilo = stevilo
                self.save()

    @property
    def datum_baze(self):
        return self.baza.datum
    
    @property
    def str_stevilo(self):
        if self.baza.tip == "inventura":
            if self.stevilo >= 0:
                return '+' + str(self.stevilo)
            else:
                return str(self.stevilo)
        elif self.baza.sprememba_zaloge == 1:
            return '+' + str(self.stevilo)
        elif self.baza.sprememba_zaloge == -1:
            return str(-self.stevilo)
    
    @property
    def ime_baze(self):
        return self.baza.title

class Vnos(models.Model):
    dimenzija = models.ForeignKey(Dimenzija,default=0,on_delete=models.CASCADE)
    tip = models.CharField(default="Y", choices=TIPI_SESTAVINE, max_length=10)
    stevilo = models.IntegerField()
    baza = models.ForeignKey(Baza,default=0, on_delete=models.CASCADE)
    cena = models.DecimalField(decimal_places=2,max_digits=5,default=None,null=True,blank=True)
    sprememba = models.ForeignKey(Sprememba,default=None,null=True,blank=True,on_delete=models.CASCADE)
    
    @property
    def skupna_cena(self):
        try:
            return self.stevilo * self.cena
        except:
            return None
            
    def doloci_ceno(self,cena = None):
        if cena == None:
            cena = float(self.vrni_sestavino().cena(self.baza.tip,self.tip))
        self.cena = cena
        self.save()

    def vrni_sestavino(self):
        dimenzija = Dimenzija.objects.get(dimenzija = self.dimenzija)
        return Sestavina.objects.get(dimenzija = dimenzija)

    def doloci_spremembo(self,sprememba):
        self.sprememba = sprememba
        self.save()

    def ustvari_spremembo(self,sestavina = None):
        if sestavina == None:
            sestavina = Sestavina.objects.get(zaloga=self.baza.zaloga, dimenzija = self.dimenzija)
        if self.baza.tip == "inventura":
            Sprememba.objects.create(
                baza = self.baza,
                zaloga = self.stevilo,
                tip = self.tip,
                sestavina = sestavina 
            )
        else:
            self.sprememba = Sprememba.objects.create(
                baza = self.baza,
                stevilo = self.stevilo,
                tip = self.tip,
                sestavina = sestavina 
            )
        self.save()

@receiver(post_save, sender=Vnos)
def create_vnos(sender, instance, created, **kwargs):
    if created:
        if instance.baza.status == "veljavno":
            sestavina = Sestavina.objects.get(zaloga = instance.baza.zaloga,dimenzija = instance.dimenzija)
            instance.ustvari_spremembo(sestavina)
            print('nov_veljaven_vnos')

@receiver(post_save, sender=Vnos)
def change_vnos(sender,instance,created,**kwargs):
    if not created:
        if instance.baza.status=="veljavno":
           print('spreminjam_veljaven_vnos')
           instance.sprememba.nastavi_iz_vnosov() 
    
@receiver(post_delete, sender=Vnos)
def delete_vnos(sender,instance,**kwargs):
    baza = instance.baza
    if baza.status == "veljavno":
        sestavina = Sestavina.objects.get(zaloga=baza.zaloga,dimenzija = instance.dimenzija)
        if baza.tip == "racun":
            sprememba = sestavina.sprememba_set.all().filter(baza__dnevna_prodaja=baza.dnevna_prodaja, tip=instance.tip).first()
        else:
            sprememba = sestavina.sprememba_set.all().filter(baza=baza, tip=instance.tip).first()
        try:
            if sprememba.vnos_set.all().count() == 0:
                sprememba.delete()
            else:
                sprememba.nastavi_iz_vnosov()
        except:
            pass
        print('brisem_vnos')

@receiver(post_save, sender=Sprememba)
def change_sprememba(sender,instance,**kwargs):
    instance.sestavina.nastavi_iz_sprememb(instance.tip)
    print('spreminjam_spremembo')

@receiver(post_delete, sender=Sprememba)
def delete_sprememba(sender,instance,**kwargs):
    instance.sestavina.nastavi_iz_sprememb(instance.tip)
    print('brisem_spremembo')

class Stroski_Group(models.Model):
    title = models.CharField(default="",max_length=20)
    tip = models.CharField(default="",max_length=20)
    datum = models.DateField(default=timezone.now)
    status = models.CharField(default="aktivno",max_length=20)
    kontejner = models.ForeignKey(Kontejner,default=None,null=True,blank=True,on_delete=models.CASCADE)

    @property
    def skupni_znesek(self):
        znesek = 0
        for strosek in self.strosek_set.all():
            znesek += strosek.znesek
        return znesek
        
class Strosek(models.Model):
    title = models.CharField(default="",max_length=20)
    group = models.ForeignKey(Stroski_Group,default=0,on_delete=models.CASCADE)
    delavec = models.ForeignKey(Zaposleni,default=None,null=True,blank=True,on_delete=models.CASCADE)
    znesek = models.DecimalField(default=0,max_digits=8,decimal_places=2)

