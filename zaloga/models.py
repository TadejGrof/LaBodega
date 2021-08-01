from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.timezone import make_aware

from datetime import datetime, time
import os
from django.contrib.auth.models import User
from program.models import BasicModel, Drzava, Oseba, Podjetje, Valuta
from prodaja.models import Stranka, Naslov
import json
from django.db.models.signals import post_save, pre_save, post_delete
from django.db.models.functions import Concat, Cast
from django.db.models import F, CharField, Value
from django.dispatch import receiver
from django.utils.timezone import now
from . import database_functions
from .model_queries import VnosZalogeQuerySet, VnosQuerySet, SestavinaQuerySet, BazaQuerySet, DobaviteljQuerySet


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

TIPI_BAZE = (
    ('inventura', 'Inventura'),
    ('prevzem','Prevzem'),
    ('prevzem_prenosa','Prevzem prenosa'),
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

PREDPONE_BAZ = {
    "inventura":"I",
    "prevzem":"P",
    "prevzem_prenosa":"PX",
    "Odpis":"O"
}

class Tip(BasicModel):
    kratko = models.CharField(max_length=10,default="")
    dolgo = models.CharField(max_length=10,default="")

    def __str__(self):
        return self.kratko

class Dimenzija(BasicModel):
    dimenzija = models.CharField(default="", max_length=20)
    radius = models.CharField(max_length=10)
    height = models.CharField(max_length=10)
    width = models.CharField(max_length=10)
    special = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['radius', 'height', 'width' , 'special']

    def __str__(self):
        return self.dimenzija

    @classmethod
    def get(radius,height,width,special=False):
        return Dimenzija.objects.filter(radius=radius,height=height,width=width,special=special).first()

class Sestavina(BasicModel):
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

class Cena(BasicModel):
    sestavina = models.ForeignKey(Sestavina, default=0, on_delete=models.CASCADE)
    cena = models.DecimalField(decimal_places=2,max_digits=5,default=0)
    valuta = models.ForeignKey(Valuta,default=None,null=True,on_delete=models.SET_NULL)

    def __str__(self):
        return str(self.sestavina) + "_" + str(self.cena) + self.valuta.simbol 

class Cenik(BasicModel):
    naziv = models.CharField(default="vele_prodaja",max_length=20)
    cene = models.ManyToManyField(Cena)

    def __str__(self):
        return self.naziv

class Zaloga(BasicModel):
    title = models.CharField(default="skladisce", max_length=20)
    tipi_sestavin = models.ManyToManyField(Tip)
    sestavine = models.ManyToManyField(Sestavina)
    ceniki = models.ManyToManyField(Cenik)

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
        return [value["dimenzija__radius"] for value in self.sestavine.values('dimenzija__radius').distinct().order_by('dimenzija__radius')]

    def zaloga_na_datum(self,sestavina,datum):
        stanje = 0
        vnosi = sestavina.vnos_set.all().filter(baza__odprema_blaga__lte=datum,baza__zaloga=self,baza__status__in=["zaklenjeno","veljavno"]).exclude(baza__tip="narocilo").all_values().order_by("odprema_blaga")
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
        vnosi = sestavina.vnos_set.all().filter(baza__odprema_blaga__gte=zacetek,baza__odprema_blaga__lte=konec,baza__zaloga=self,baza__status__in=["zaklenjeno","veljavno"]).exclude(baza__tip="narocilo").all_values().order_by("datum")
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
    def vrni_sestavine(self):
        return self.sestavina_set.all()

class Zaposleni(BasicModel):
    oseba = models.OneToOneField(Oseba,default=None,blank=True,null=True,on_delete=models.CASCADE)
    user = models.OneToOneField(User,default=None,blank=True,null=True,on_delete=models.CASCADE)

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

class VnosZaloge(BasicModel):
    zaloga = models.ForeignKey(Zaloga, default=1,on_delete=models.CASCADE)
    sestavina = models.ForeignKey(Sestavina,default=1,on_delete=models.CASCADE)
    stanje = models.IntegerField(default=0)
    
    objects = VnosZalogeQuerySet.as_manager()

    class Meta:
        ordering = ['zaloga','sestavina']

###################################################################################################

class Kontejner(BasicModel):
    stevilka = models.CharField(default="", max_length=20)

##################################################################################################

class Dnevna_prodaja(BasicModel):
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
        return self.baza_set.filter(tip='racun',status='veljavno').order_by('-uveljavitev').prefetch_related('vnos_set')

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

class Stranka2(BasicModel):
    podjetje = models.OneToOneField(Podjetje,null=True,blank=True,on_delete=models.CASCADE)
    status = models.CharField(default='aktivno',max_length=10)

    def __str__(self):
        return self.podjetje.naziv if self.podjetje != None else "/"
        
    @property
    def ima_aktivno_prodajo(self):
        return self.baza_set.all().filter(status="aktivno").exists()

    @property
    def aktivna_prodaja(self):
        return self.baza_set.all().filter(status="aktivno").first()

    
class Dobavitelj(BasicModel):
    podjetje = models.OneToOneField(Podjetje,default=0,on_delete=models.CASCADE)

    objects = DobaviteljQuerySet.as_manager()

    def __str__(self):
        return self.podjetje.naziv

class Baza(BasicModel):
    author = models.ForeignKey(User,default=1, on_delete=models.CASCADE)
    title = models.CharField(default="",max_length=15)
    datum = models.DateField(default=timezone.now)
    odprema_blaga = models.DateTimeField(default=timezone.now)
    uveljavitev = models.DateTimeField(default=timezone.now)
    zaloga = models.ForeignKey(Zaloga, default=1 ,on_delete=models.CASCADE)
    status = models.CharField(default="aktivno",max_length=10)
    sprememba_zaloge = models.IntegerField(default = -1)
    tip = models.CharField(default="prevzem",max_length=20, choices=TIPI_BAZE)
    stevilka = models.IntegerField(default=0)
    dobavitelj = models.ForeignKey(Dobavitelj,null=True,default=None,blank=True, on_delete=models.CASCADE)
    kontejner = models.OneToOneField(Kontejner,null=True,default=None,blank=True, on_delete=models.CASCADE)
    popust = models.IntegerField(default = None, null=True, blank=True)
    stranka = models.ForeignKey(Stranka, on_delete=models.CASCADE, default=None, null=True, blank=True)
    dnevna_prodaja = models.ForeignKey(Dnevna_prodaja, on_delete=models.CASCADE, default=None, null=True, blank=True)
    prevoz = models.DecimalField(default=None,null=True,blank=True,max_digits=5, decimal_places=2)
    zalogaPrenosa = models.IntegerField(default=None,null=True,blank=True)
    cena = models.DecimalField(default=None,decimal_places = 2,max_digits=10,null=True,blank=True)
    ladijski_prevoz = models.DecimalField(default=None,decimal_places = 2,max_digits=10,null=True,blank=True)
    placilo = models.DecimalField(default=None,decimal_places = 2,max_digits=10,null=True,blank=True)
    
    objects = BazaQuerySet.as_manager()

    def __str__(self):
        return self.title

    @property 
    def getZalogaPrenosa(self):
        return Zaloga.objects.get(id=self.zalogaPrenosa)

    @property
    def vrni_vnose(self):
        return self.vnos_set.all()

    @property
    def vnosi_values(self):
        return self.vnos_set.all().all_values()

    @property
    def cena_nakupa(self):
        return sum([vnos["skupna_cena_nakupa"] for vnos in self.vnosi_values])

    @property
    def skupna_cena_prodaje(self):
        return sum([vnos["skupna_cena"] for vnos in self.vnosi_values])

    @property
    def stevilo_vnosov(self):
        return self.vnos_set.all().count()

    @property
    def zasluzek(self):
        return float(self.skupna_cena_prodaje) - float(self.cena_nakupa)

    @property
    def povprecna_cena(self):
        cena = self.cena if self.cena != None else 0
        return round(cena / self.skupno_stevilo, 2) if self.skupno_stevilo != 0 else 0

    @property
    def skupno_stevilo(self, tip=None):
        if tip == None:
            return sum([vnos["stevilo"] for vnos in self.vnos_set.all().values("stevilo")])
        else:
            return sum([vnos["stevilo"] for vnos in self.vnos_set.filter(sestavina__tip = tip).values("stevilo")])

    @property
    def skupna_cena(self, tip=None):
        if tip == None:
            return sum([vnos.skupna_cena for vnos in self.vnos_set.all()])
        else:
            return sum([vnos.skupna_cena for vnos in self.vnos_set.filter(sestavina__tip = tip)])

    @property
    def cena_popusta(self):
        return round(float(self.skupna_cena) * (self.popust / 100)) if self.popust != None else 0

    @property
    def cena_prevoza(self):
        return round(float(self.skupno_stevilo * self.prevoz)) if self.prevoz != None else 0
    
    @property
    def koncna_cena(self):
        return self.skupna_cena - self.cena_popusta + self.cena_prevoza

    def doloci_title(self,stevilo=None):
        leto = self.datum.year
        if stevilo == None:
            stevilo = Baza.objects.filter(datum__year=leto).order_by("stevilka").last().stevilka + 1
        if self.tip == "racun":
            title = str(stevilo)
            while len(title) != 5:
                title = "0" + title
            return str(leto)[:2] + title
        elif self.tip == "vele_prodaja":
            return str(stevilo) + "/" + str(leto)
        else:
            title = PREDPONE_BAZ[self.title] + "-" + str(leto) + "-" + str(stevilo)
        
    def doloci_datum(self,datum):
        if datum == None:
            if self.tip == "racun":
                self.datum = self.dnevna_prodaja.datum
            else:
                self.datum = self.uveljavitev.date()
        else:
            self.datum = datum

    def doloci_uveljavitev(self):
        self.uveljavitev = timezone.localtime(timezone.now())

    def doloci_odpremo_blaga(self,datum = None):
        if datum == None:
            if self.tip == "racun":
                datum = self.dnevna_prodaja.datum
            else:
                datum = self.datum
        if self.tip in ["prevzem","prenos"]:
            cas = time(8,0,0)
        elif self.tip == "inventura":
            cas = time(20,0,0)
        elif self.tip == "racun":
            cas = self.uveljavitev.time()
        else:
            cas = time(12,0,0)
        self.odprema_blaga = make_aware(datetime.combine(datum,cas))


    def kopiraj_vnose(self,baza):
        self.vnos_set.all().delete()
        for vnos in baza.vnos_set.all():
            Vnos.objects.create(
                baza=self,
                sestavina=vnos.sestavina,
                stevilo=vnos.stevilo,
                cena=vnos.cena
            )

    def uveljavi(self,delno=False,datum=None,odprema_blaga=None):
        self.status = "veljavno"
        self.doloci_uveljavitev()
        self.doloci_datum(datum)
        self.doloci_odpremo_blaga(odprema_blaga)
        self.doloci_title()
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

    def uveljavi_inventuro(self,delno = False):
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
        baza_prenosa = Baza.objects.create(
                zaloga_id = self.getZalogaPrenosa.pk,
                tip = "prevzem",
                sprememba_zaloge = 1,
                author = self.author,
                zalogaPrenosa = self.zaloga.pk
            )
        baza_prenosa.kopiraj_vnose(self)
        baza_prenosa.uveljavi_bazo()

    # Ustvari nove vnose z trenutnim stanjem zaloge
    # Uporaba izključno v bazi tipa 'inventura'
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

class Vnos(BasicModel):
    sestavina = models.ForeignKey(Sestavina,default=None,null=True,blank=True, on_delete=models.CASCADE)
    stevilo = models.IntegerField(default=1)
    baza = models.ForeignKey(Baza,default=0, on_delete=models.CASCADE)
    cena = models.DecimalField(decimal_places=2,max_digits=5,default=None,null=True,blank=True)
    cena_nakupa = models.DecimalField(decimal_places=2,max_digits=5,default=None,null=True,blank=True)

    objects = VnosQuerySet.as_manager()

    @property
    def skupna_cena(self):
        return self.stevilo * self.cena if self.ceno != None else 0
            
    @property
    def skupna_cena_nakupa(self):
        return self.stevilo * self.cena_nakupa if self.cena_nakupa != None else 0

    def doloci_ceno(self,cena = None):
        if cena == None:
            cena = float(self.vrni_sestavino().cena(self.baza.tip,self.tip))
            self.cena = cena
            self.save()


@receiver(pre_save, sender=Vnos)
def save_vnos(sender,instance,**kwargs):
    print("VNOS SHRANJEN DELAM NASTAVI IZ VNOSOV")
    if instance.pk != None:
        baza = instance.baza
        if baza.status == "veljavno":
            old_vnos = Vnos.objects.get(id=instance.id)
            if old_vnos.stevilo != instance.stevilo:
                print("SPREMEMBA STEVILA")
                baza.zaloga.nastavi_iz_vnosov(instance.sestavina)
            elif old_vnos.sestavina != instance.sestavina:
                print("SPREMEMBA SESTAVINE")
                baza.zaloga.nastavi_iz_vnosov(old_vnos.sestavina)
                baza.zaloga.nastavi_iz_vnosov(instance.sestavina)

@receiver(post_save, sender=Vnos)
def create_vnos(sender, instance, created, **kwargs):
    if created:
        baza = instance.baza
        if baza.status == "veljavno":
            baza.zaloga.nastavi_iz_vnosov(instance.sestavina)

@receiver(post_delete, sender=Vnos)
def delete_vnos(sender,instance,**kwargs):
    baza = instance.baza
    if baza.status == "veljavno":
        baza.zaloga.nastavi_iz_vnosov(instance.sestavina)

class Stroski_Group(BasicModel):
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
        
class Strosek(BasicModel):
    title = models.CharField(default="",max_length=20)
    group = models.ForeignKey(Stroski_Group,default=0,on_delete=models.CASCADE)
    delavec = models.ForeignKey(Zaposleni,default=None,null=True,blank=True,on_delete=models.CASCADE)
    znesek = models.DecimalField(default=0,max_digits=8,decimal_places=2)

