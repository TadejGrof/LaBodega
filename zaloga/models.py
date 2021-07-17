from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db import models
from django.utils import timezone

from datetime import datetime
import os
from django.contrib.auth.models import User
from prodaja.models import Stranka, Naslov
import json
from django.db.models.signals import post_save, pre_save, post_delete
from django.db.models.functions import Concat, Cast
from django.db.models import F, CharField, Value
from django.dispatch import receiver
from django.utils.timezone import now
from . import database_functions
from .model_queries import VnosZalogeQuerySet, VnosQuerySet, SestavinaQuerySet


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
    ('poland',"Poland"),
    ('sweden',"Sweden"),
    ('zoki',"Zoki"),
)

DRZAVE = (
    ('slo', 'Slovenia'),
    ('jap', 'Japan'),
    ('pol', 'Poland'),
    ('ang', 'England'),
    ('kor', 'Korea'),
    ('pan', 'Panama'),
    ('swe',"Sweden"),
    ('sui',"Switzerland")
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


class Tip(models.Model):
    kratko = models.CharField(max_length=10,default="")
    dolgo = models.CharField(max_length=10,default="")

    def __str__(self):
        return self.kratko

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

class Sestavina(models.Model):
    dimenzija = models.ForeignKey(Dimenzija, on_delete=models.CASCADE)
    tip = models.ForeignKey(Tip,default=None,null=True,blank=True,on_delete=models.CASCADE)

    objects = SestavinaQuerySet.as_manager()

    class Meta:
        ordering = ['dimenzija','tip']

    def __str__(self):
        try:
            return self.dimenzija.dimenzija + "_" + self.tip.kratko
        except:
            return self.dimenzija.dimenzija

    def nastavi_iz_sprememb(self,tip):
        zaklep = self.zaloga.zaklep_zaloge
        datum = zaklep.datum
        stanje = zaklep.vrni_stanje(self,tip)
        spremembe = self.sprememba_set.all().filter(tip = tip,baza__datum__gt = datum).order_by('baza__datum','baza__cas').values(
            "stevilo",
            "baza__sprememba_zaloge",
            "stanje"
        )
        for sprememba in spremembe:
            if sprememba["stanje"] == None:
                stanje += sprememba["stevilo"] * sprememba["baza__sprememba_zaloge"]
            else:
                stanje = sprememba["stanje"]
        setattr(self,tip,stanje)
        self.save()

    def zaloga_na_datum(self,datum,tip):
        if isinstance(datum,str):
            datum = datum.split("-")
            datum = datetime(int(datum[0]),int(datum[1]),int(datum[2])).date()
        spremembe = self.sprememba_set.all().filter(tip = tip)
        zaloga = self.zaloga
        zaklep = zaloga.zaklep_zaloge
        stanje = zaloga.zaklep_zaloge.vrni_stanje(self,tip)

        if zaklep.datum < datum:
            spremembe = spremembe.filter(baza__datum__gt = zaklep.datum, baza__datum__lte = datum).order_by('baza__datum','baza__cas')
            spremembe = spremembe.values("stanje","stevilo", "baza__sprememba_zaloge")
            for sprememba in spremembe:
                if sprememba["stanje"] == None:
                    stanje += sprememba["stevilo"] * sprememba["baza__sprememba_zaloge"]
                else:
                    stanje = sprememba["stanje"]
        # gledamo od zaklepa navzdol:
        elif zaklep.datum > datum:
            spremembe = spremembe.filter(baza__datum__lte = zaklep.datum, baza__datum__gte = datum).order_by('-baza__datum','-baza__cas')
            spremembe = spremembe.values("stanje","stevilo", "baza__sprememba_zaloge")
            for sprememba in spremembe:
                if sprememba["stanje"] == None:
                    stanje -= sprememba["stevilo"] * sprememba["baza__sprememba_zaloge"]
                else:
                    stanje = sprememba["stanje"]
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

class Cena(models.Model):
    sestavina = models.ForeignKey(Sestavina, default=0, on_delete=models.CASCADE)
    cena = models.DecimalField(decimal_places=2,max_digits=5,default=0)
    nacin = models.CharField(max_length=10, choices=TIPI_CEN, default="prodaja")
    tip = models.CharField(max_length=4, choices=TIPI_SESTAVINE, default="Y")
    prodaja = models.CharField(max_length=15, choices=TIPI_PRODAJE, null=True, blank=True, default=None)
    drzava = models.CharField(max_length=15, choices=DRZAVE, null=True,blank=True,default=None)
    
class Zaloga(models.Model):
    title = models.CharField(default="skladisce", max_length=20)
    tipi_prodaje = models.CharField(default='["vele_prodaja"]', max_length=50)
    tipi_sestavine = models.CharField(default='["Y","W","JP","JP50","JP70"]', max_length=50)
    tipi_sestavin = models.ManyToManyField(Tip)
    sestavine = models.ManyToManyField(Sestavina)
    cenik = models.ManyToManyField(Cena)

    def __str__(self):
        return self.title

    @property
    def tipi_prodaj(self):
        return json.loads(self.tipi_prodaje)

    @property
    def danes(self):
        return datetime.today().strftime('%Y-%m-%d')

    @property
    def vrni_razlicne_radiuse(self):
        razlicni_radiusi = []
        for radius in self.sestavine.values('dimenzija__radius').distinct().order_by('dimenzija__radius'):
                razlicni_radiusi.append(radius['dimenzija__radius'])
        return razlicni_radiusi

    def zaloga_na_datum(self,sestavina,datum):
        stanje = 0
        vnosi = sestavina.vnos_set.all().filter(baza__datum__lte=datum,baza__zaloga=self,baza__status__in=["zaklenjeno","veljavno"]).exclude(baza__tip="narocilo").all_values().order_by("datum")
        for vnos in vnosi:
            if vnos["sprememba_zaloge"] == 0:
                stanje = vnos["stevilo"]
            else:
                stanje += vnos["stevilo"] * vnos["sprememba_zaloge"]
        return stanje

    def danasnja_prodaja(self):
        return self.dnevna_prodaja_set.all().filter(datum=datetime.today()).first()

    def vrni_stanja(self,sestavina,zacetek,konec):
        zaporedna_stanja = []
        vnosi = sestavina.vnos_set.all().filter(baza__datum__gte=zacetek,baza__datum__lte=konec,baza__zaloga=self,baza__status__in=["zaklenjeno","veljavno"]).exclude(baza__tip="narocilo").all_values().order_by("datum")
        stanje = self.zaloga_na_datum(sestavina,zacetek)
        for vnos in vnosi:
            if vnos["sprememba_zaloge"] == 0:
                stanje = vnos["stevilo"]
            else:
                stanje += vnos["stevilo"] * vnos["sprememba_zaloge"]
            vnos["stanje"] = stanje
        return vnosi

    def nastavi_iz_vnosov(self,sestavina):
        stanje = self.zaloga_na_datum(sestavina,datetime.now())
        vnos_zaloge = self.vnoszaloge_set.all().get(sestavina=sestavina)
        if vnos_zaloge.stanje != stanje:
            vnos_zaloge.stanje = stanje
            vnos_zaloge.save()
            print("POPRAVLJAM VNOS ZALOGE ZA " + str(sestavina))

    @property
    def vrni_tipe(self):
        return [tip.kratko for tip in self.tipi_sestavin.all()]

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
        return self.sestavine.all().order_by("dimenzija")\
        .values().annotate(radius = F("dimenzija__radius"),dim = F("dimenzija__dimenzija"))

    @property
    def vrni_sestavine(self):
        return self.sestavina_set.all()

    @property
    def zaklep_zaloge(self):
        return self.zaklep_set.all().first()

    @property
    def datum_zaklepa(self):
        return self.zaklep_zaloge.datum


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

    def remove_key(self,key):
        stanja = self.stanja
        stanja.pop(key,None)
        self.stanja_json = json.dumps(stanja)
        self.save()

    def nastavi_stanje(self,sestavina,tip,stanje = 0):
        stanja = self.stanja
        if str(sestavina.pk) in stanja:
            stanja[str(sestavina.pk)][tip] = stanje
        else:
            stanja[str(sestavina.pk)] = {tip:stanje}
        self.stanja_json = json.dumps(stanja)
        self.save()
        return stanja

@receiver(post_save, sender=Zaklep)
def create_zaklep(sender, instance, created, **kwargs):
    if created:
        baze = instance.zaloga.baza_set.all().filter(status = "veljavno", datum__lte = instance.datum)
        for baza in baze:
            baza.status = "zaklenjeno"
        Baza.objects.bulk_update(baze,["status"])


class Zaposleni(models.Model):
    user = models.OneToOneField(User,default=None,blank=True,null=True,on_delete=models.CASCADE)
    zaloga = models.ForeignKey(Zaloga,default=1,on_delete=models.CASCADE)
    ime = models.CharField(default="/",max_length=20)
    priimek = models.CharField(default="/",max_length=20)
    davcna = models.CharField(default="/", max_length=30)
    naslov = models.OneToOneField(Naslov, default=None, on_delete=models.CASCADE, null=True, blank=True)
    telefon = models.CharField(default="/", max_length=20)
    mail = models.CharField(default="/", max_length=40)

##################################################################################################


@receiver(post_save, sender=Tip)
def create_tip(sender, instance, created, **kwargs):
    if created:
        for dimenzija in Dimenzija.objects.all():
            Sestavina.objects.create(dimenzija=dimenzija,tip=instance)

@receiver(post_save, sender=Dimenzija)
def create_dimenzija(sender, instance, created, **kwargs):
    if created:
        for tip in Tip.objects.all():
            sestavina = Sestavina.objects.create(dimenzija=instance,tip=tip)

@receiver(post_save, sender=Sestavina)
def create_sestavina(sender, instance, created, **kwargs):
    if created:
        for zaloga in Zaloga.objects.all():
            VnosZaloge.objects.create(zaloga=zaloga,sestavina=instance)        

class VnosZaloge(models.Model):
    zaloga = models.ForeignKey(Zaloga, default=1,on_delete=models.CASCADE)
    sestavina = models.ForeignKey(Sestavina,default=1,on_delete=models.CASCADE)
    stanje = models.IntegerField(default=0)
    
    objects = VnosZalogeQuerySet.as_manager()

    class Meta:
        ordering = ['zaloga','sestavina']

###################################################################################################

class Kontejner(models.Model):
    stevilka = models.CharField(default="", max_length=20)
    posiljatelj = models.CharField(default="", max_length=20, choices=POSILJATELJI)
    drzava = models.CharField(default="", max_length=20, choices=DRZAVE)

##################################################################################################

class Dnevna_prodaja(models.Model):
    zaloga = models.ForeignKey(Zaloga, default=1, on_delete=models.CASCADE)
    datum = models.DateField(default=timezone.now)
    title = models.CharField(default="", max_length=20)
    tip = models.CharField(default="Aktivno",max_length=20,null=True,blank=True)
    
    @property
    def stevilo_racunov(self):
        return self.racun_set.all().count()

    @property
    def stevilo_veljavnih_racunov(self):
        return self.racun_set.all().filter(status='veljavno').count()

    @property
    def aktivni_racun(self):
        return self.baza_set.all().filter(tip='racun', status = "aktivno").first()

    @property
    def dan(self):
        return self.datum

    def doloci_tip(self):
        dan_v_tednu = self.datum.weekday()
        if dan_v_tednu == 5 or dan_v_tednu == 6:
            self.tip = "Vikend"
        else:
            self.tip = "Aktivno"
        self.save()
        
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
        return Vnos.objects.filter(baza__dnevna_prodaja = self, baza__status="veljavno")

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
        for vnos in self.urejeni_vnosi.order_by("sestavina"):
            if vnos.sestavina in prodane:
                prodane[vnos.sestavina]['stevilo'] += vnos.stevilo
                prodane[vnos.sestavina]['cena'] += vnos.cena * vnos.stevilo
            else:
                slovar = {'stevilo':vnos.stevilo,'cena':vnos.cena * vnos.stevilo}
                prodane.update({vnos.sestavina:slovar})
        return prodane

    @property
    def activity_log(self):
        activity_log = []
        for racun in self.racuni:
            for vnos in racun.vnos_set.all():
                activity_log.append({
                    'dimenzija':vnos.sestavina.dimenzija,
                    'stevilo':vnos.stevilo,
                    'tip':vnos.sestavina.tip,
                    'cena':vnos.stevilo * vnos.cena,
                    'cas': racun.cas,
                })
        return activity_log

    def nov_racun(self,author=None):
        baza = Baza.objects.create(
            zaloga = self.zaloga,
            title= "Aktiven racun",
            tip='racun',
            dnevna_prodaja = self,
            popust = 0)
        if author != None:
            baza.author = author
            baza.save()

@receiver(post_save, sender=Dnevna_prodaja)
def create_dnevna_prodaja(sender, instance, created, **kwargs):
    if created:
        instance.doloci_title()
        instance.doloci_tip()
        Baza.objects.create(
            zaloga = instance.zaloga,
            title = "Aktiven racun",
            tip='racun',
            dnevna_prodaja = instance,
            popust = 0 )

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
    zalogaPrenosa = models.IntegerField(default=None,null=True,blank=True)
    cena = models.DecimalField(default=None,decimal_places = 2,max_digits=10,null=True,blank=True)
    ladijski_prevoz = models.DecimalField(default=None,decimal_places = 2,max_digits=10,null=True,blank=True)
    placilo = models.DecimalField(default=None,decimal_places = 2,max_digits=10,null=True,blank=True)
    
    @property 
    def getZalogaPrenosa(self):
        return Zaloga.objects.get(id=self.zalogaPrenosa)

    def __str__(self):
        return self.title

    #def save(self, *args, **kwargs):
    #    baza = Baza.objects.get(pk = self.pk)
    #    print(baza.prevoz)
    #    print(self.prevoz)
    #    super(Baza, self).save(*args, **kwargs)

    def skupnoStevilo(self,tip):
        skupno = 0
        for vnos in self.vnos_set.all().all_values():
            if vnos["tip_id"] == tip.id:
                skupno += vnos["stevilo"]
        return skupno

    def skupnaCena(self,tip):
        skupno = 0
        for vnos in self.vnosi_values:
            if vnos["tip"] == tip:
                skupno += vnos["cena"] * vnos["stevilo"]
        return skupno

    def uveljavi_inventuro(self,delno = False):
        print("uveljavljam inventuro")
        vnosi_zaloge = []
        for sestavina in self.zaloga.sestavine.all():
            vnos = self.vnos_set.all().filter(sestavina = sestavina).first()
            if vnos == None and not delno:
                vnos_zaloge = sestavina.vnoszaloge_set.all().get(zaloga=self.zaloga)
                vnos_zaloge.stanje = 0
                vnosi_zaloge.append(vnos_zaloge)
            elif vnos != None:
                vnos_zaloge = sestavina.vnoszaloge_set.all().get(zaloga=self.zaloga)
                vnos_zaloge.stanje = vnos.stevilo
                vnosi_zaloge.append(vnos_zaloge)
        VnosZaloge.objects.bulk_update(vnosi_zaloge,["stanje"])

           
    def uveljavi_prenos(self,cas = None):
        self.uveljavi_bazo()
        self.status = "zaklenjeno"
        self.save()
        bazaPrenosa = Baza.objects.create(
                zaloga_id = self.getZalogaPrenosa.pk,
                tip = "prevzem",
                sprememba_zaloge = 1,
                title = self.title.replace("PS","PX"),
                author = self.author,
                zalogaPrenosa = self.zaloga.pk
            )
        for vnos in self.vnos_set.all().iterator():
            bazaPrenosa.dodaj_vnos(vnos.sestavina,vnos.stevilo)
        bazaPrenosa.save()
        bazaPrenosa.uveljavi_bazo()
        bazaPrenosa.status = "zaklenjeno"
        bazaPrenosa.save()

    def uveljavi_racun(self):
        for vnos in self.vnos_set.all():
            sestavina = Sestavina.objects.get(zaloga = self.zaloga, dimenzija = vnos.dimenzija)
            sprememba = Sprememba.objects.filter(baza__dnevna_prodaja = self.dnevna_prodaja, sestavina = sestavina, tip = vnos.tip ).first()
            if sprememba == None:
                sprememba = Sprememba.objects.create(
                    sestavina = sestavina,
                    tip = vnos.tip,
                    stevilo = vnos.stevilo,
                    baza = self)
            vnos.sprememba = sprememba
            vnos.save()

    @property
    def posiljatelj(self):
        if self.kontejner != None:
            return self.kontejner.get_drzava_display()
        elif self.zalogaPrenosa != None:
            return Zaloga.objects.get(pk = self.zalogaPrenosa).title
        return None
        
    @property
    def tipPrevzema(self):
        if self.kontejner != None:
            return "Kontejner"
        elif self.zalogaPrenosa != None:
            return "Prenos"
        return "Drugo"

    def uveljavi(self,delno=False,datum=None,cas=None):
        self.status = "veljavno"
        self.doloci_cas(cas)
        self.doloci_datum(datum)
        self.save()
        if self.tip == "inventura":
            self.uveljavi_inventuro(delno)
        elif self.tip == "prenos":
            self.uveljavi_prenos()
        else:
            self.uveljavi_bazo()

    def uveljavi_bazo(self):
        vnosi = self.vnos_set.all().order_by("sestavina")
        vnosi_zaloge = []
        for vnos in vnosi:
            vnos_zaloge = vnos.sestavina.vnoszaloge_set.all().get(zaloga = self.zaloga)
            vnos_zaloge.stanje = vnos_zaloge.stanje + vnos.stevilo * self.sprememba_zaloge
            if len(vnosi_zaloge) == 0 or vnosi_zaloge[-1] != vnos_zaloge:
                vnosi_zaloge.append(vnos_zaloge)
        VnosZaloge.objects.bulk_update(vnosi_zaloge,["stanje"])  

    def dodaj_vnos(self,sestavina,stevilo,cena_prodaje = None,cena_nakupa = None,):
        vnos = Vnos.objects.create(sestavina=sestavina,stevilo=stevilo,baza=self,cena=cena_prodaje,cena_nakupa=cena_nakupa)
        if self.status == 'veljavno':
            self.zaloga.nastavi_iz_vnosov(sestavina)
        return vnos

    def doloci_cas(self,cas):
        if cas == None:
            self.cas = timezone.localtime(timezone.now())
        else:
            self.cas = cas

    def doloci_datum(self,datum):
        if datum == None:
            self.datum = timezone.localtime(timezone.now())
        else:
            self.datum = datum

    @property
    def slovar_dosedanjih_kupljenih(self):
        kupljene = self.dosedanje_kupljene_stranke
        slovar = {}
        for kupljena in kupljene:
            slovar[kupljena["dimenzija_tip"]] = True
        return slovar

    @property
    def dosedanje_kupljene_stranke(self):
        if self.tip == "vele_prodaja":
            return Vnos.objects.filter(baza__stranka = self.stranka)\
            .order_by("dimenzija").values("dimenzija__dimenzija","tip")\
            .annotate(dimenzija_tip = Concat(F("dimenzija__dimenzija"),Value("_"),F("tip")))\
            .values("dimenzija_tip").distinct()
        return []


    @property
    def vrni_vnose(self):
        return self.vnos_set.all()

    @property
    def vnosi_values(self):
        return self.vnos_set.all().all_values()

    @property
    def cena_nakupa(self):
        vnosi = self.vnosi_values
        cena = 0
        for vnos in vnosi:
            cena += vnos["skupna_cena_nakupa"]
        return cena

    @property
    def skupna_cena_prodaje(self):
        vnosi = self.vnosi_values
        cena = 0
        for vnos in vnosi:
            cena += vnos["skupna_cena"]
        return cena

    @property
    def stevilo_vnosov(self):
        return self.vnos_set.all().count()

    @property
    def zasluzek(self):
        return float(self.skupna_cena_prodaje) - float(self.cena_nakupa)

    @property
    def povprecna_cena(self):
        cena = self.cena
        if cena == None:
            cena = 0
        try:
            return round(cena / self.skupno_stevilo, 2)
        except:
            return 0

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
        slovar_kupljenih = self.slovar_dosedanjih_kupljenih
        print(slovar_kupljenih)
        for sestavina in self.zaloga.vrni_zalogo:
            for tip in self.zaloga.vrni_tipe:
                count += 1
                slovar = {'dimenzija': sestavina['dim'],
                        'tip': tip[0],
                        'zaloga': sestavina[tip[0]],
                        'radius': sestavina['radius'],
                        'pk': count,
                        'vneseno':False,
                        'pk_vnosa':None,
                        'stevilo':None
                }
                try:
                    slovar["kupljena"] = slovar_kupljenih[sestavina["dim"] + "_" + tip[0]]
                except:
                    slovar["kupljena"] = False 
                vnosi.update({sestavina['dim'] + '_' + tip[0]: slovar})
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

    def nastavi_vnose_inventure(self):
        vnosi = []
        vnos_set = self.vnos_set.all()
        for sestavina in self.zaloga.sestavine.all().zaloga_values(self.zaloga).all_values():
            if not vnos_set.filter(sestavina__id=sestavina["id"]).exists():
                vnosi.append(Vnos(
                    baza=self,
                    sestavina_id = sestavina["id"],
                    stevilo = sestavina["stanje"]
                ))
        Vnos.objects.bulk_create(vnosi)

###################################################################################################
class SpremembaZaloge:
    def __init__(self):
        self.vnosi = []
        self.dnevna_prodaja = None
        self.baza = None
        self.stevilo = 0

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
    sestavina = models.ForeignKey(Sestavina,default=None,null=True,blank=True, on_delete=models.CASCADE)
    stevilo = models.IntegerField(default=1)
    baza = models.ForeignKey(Baza,default=0, on_delete=models.CASCADE)
    cena = models.DecimalField(decimal_places=2,max_digits=5,default=None,null=True,blank=True)
    sprememba = models.ForeignKey(Sprememba,default=None,null=True,blank=True,on_delete=models.CASCADE)
    cena_nakupa = models.DecimalField(decimal_places=2,max_digits=5,default=None,null=True,blank=True)

    objects = VnosQuerySet.as_manager()

    @property
    def skupna_cena(self):
        try:
            return self.stevilo * self.cena
        except:
            return 0
            
    @property
    def skupna_cena_nakupa(self):
        try:
            return self.stevilo * self.cena_nakupa
        except:
            return 0

    def doloci_ceno(self,cena = None):
        if cena == None:
            cena = float(self.vrni_sestavino().cena(self.baza.tip,self.tip))
        self.cena = cena
        self.save()

    def spremeni_stevilo(self,stevilo):
        razlika = self.stevilo - stevilo
        if razlika != 0:
            self.stevilo = stevilo
            self.save()
        if self.baza.status == "veljavno":
            self.baza.zaloga.nastavi_iz_vnosov(self.sestavina)

    def spremeni_tip(self,tip):
        if tip != self.tip:
            nova_sestavina = Sestavina.objects.get(dimenzija=self.sestavina.dimenzija,tip=tip)
            stara_sestavina = self.sestavina
            self.sestavina = nova_sestavina
            self.save()
        if self.baza.status == "veljavno":
            self.baza.zaloga.nastavi_iz_vnosov([nova_sestavina,stara_sestavina])

@receiver(post_delete, sender=Vnos)
def delete_vnos(sender,instance,**kwargs):
    baza = instance.baza
    if baza.status == "veljavno":
        baza.zaloga.nastavi_iz_vnosov(instance.sestavina)

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

