from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.db import models
from django.utils import timezone
from datetime import datetime
import os
from django.contrib.auth.models import User
from prodaja.models import Prodaja, Stranka
from program.models import Program
import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from .funkcije import ustvari_zacetna_stanja, arhiv_baz, arhiv_prodaj, zacetna_stanja

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

    def __str__(self):
        return self.title

    @property
    def danes(self):
        return datetime.today().strftime('%Y-%m-%d')

    @property
    def zaloga(self):
        dimenzije = self.vrni_slovar_dimenzij(True)
        zaloga = {}
        for sestavina in self.sestavina_set.all().values():
            dimenzija = dimenzije[sestavina['dimenzija_id']]
            zaloga.update({dimenzija:{}})
            for tip in self.vrni_tipe:
                zaloga[dimenzija].update({tip[0]:sestavina[tip[0]]})
        return zaloga
                

    @property
    def vrni_razlicne_radiuse(self):
        razlicni_radiusi = []
        for radius in self.sestavina_set.all().values('dimenzija__radius').distinct().order_by('dimenzija__radius'):
            razlicni_radiusi.append(radius['dimenzija__radius'])
        return razlicni_radiusi

    @property
    def vrni_dimenzije(self):
        return Dimenzija.objects.all().values_list('dimenzija','radius','height','width','special')

    def dodaj_sestavino(self,dimenzija,radius,height,width,special=False,white=0,yellow=0):
        dimenzija = Dimenzija.objects.create(dimenzija=dimenzija,radius=radius,height=height,width=width,special=special)
        Sestavina.objects.create(zaloga=self,dimenzija=dimenzija,white=white,yellow=yellow)

    @property
    def zacetna_stanja(self):
        with open('zacetna_stanja.json') as dat:
            slovar = json.load(dat)
        return slovar

    def ponastavi_zalogo(self):
        for sestavina in self.sestavina_set.all():
            for tip in self.vrni_tipe:
                setattr(sestavina,tip[0],0)
            sestavina.save()

    def zakleni_zalogo(self,datum):
        ustvari_zacetna_stanja(self,datum)
        baze = self.baza_set.all().filter(datum__lte = datum, status="veljavno").exclude(tip = "racun")
        arhiv_baz(baze)
        prodaje = self.dnevna_prodaja_set.all().filter(datum__lte = datum)
        arhiv_prodaj(prodaje)
        baze.update(status="zaklenjeno") 
        baze = self.baza_set.all().filter(status="zaklenjeno")
        spremembe = Sprememba.objects.filter(baza__in = baze)
        spremembe.delete()
        for prodaja in prodaje:
            racuni = prodaja.baza_set.all().filter(status="veljavno",tip="racun")
            racuni.update(status="zaklenjeno") 
            Sprememba.objects.filter(baza__dnevna_prodaja = prodaja).delete()
        return 

    def ustvari_cene(self):
        for sestavina in self.sestavina_set.all():
            for tip in TIPI_SESTAVINE:
                for prodaja in TIPI_PRODAJE:
                    Cena.objects.create(sestavina = sestavina, tip = tip[0], prodaja = prodaja[0])

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
    dimenzija = models.OneToOneField(Dimenzija, on_delete=models.CASCADE)
    Y = models.IntegerField(default = 0)
    W = models.IntegerField(default = 0)  
    JP = models.IntegerField(default = 0)
    JP50 = models.IntegerField(default = 0)
    JP70 = models.IntegerField(default = 0)

    class Meta:
        ordering = ['dimenzija']

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


    def __str__(self):
        return self.dimenzija.dimenzija

    @property
    def prijazna_dimenzija(self):
        return self.dimenzija.dimenzija.replace('/','-')

    def nastavi_iz_sprememb(self,tip):
        spremembe = self.sprememba_set.all().filter(tip=tip).order_by('baza__datum','baza__cas')
        stanje = self.zaloga.zacetna_stanja[self.dimenzija.dimenzija][tip]
        for sprememba in spremembe:
            if sprememba.stanje == None:
                stanje += sprememba.stevilo * sprememba.baza.sprememba_zaloge
            else:
                stanje = sprememba.stanje
        setattr(self,tip,stanje)
        self.save()

    def zaloga_na_datum(self,datum,tip):
        spremembe = self.sprememba_set.all().filter(baza__datum__lte = datum, tip = tip).order_by('baza__datum','baza__cas')
        stanje = self.zaloga.zacetna_stanja[self.dimenzija.dimenzija][tip]
        for sprememba in spremembe:
            if sprememba.stanje == None:
                stanje += sprememba.stevilo * sprememba.baza.sprememba_zaloge
            else:
                stanje = sprememba.stanje
        return stanje

    def vrni_stanja(self,tip):
        spremembe = self.sprememba_set.all().filter(tip=tip).order_by('baza__datum','baza__cas')
        stanje = self.zaloga.zacetna_stanja[self.dimenzija.dimenzija][tip]
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


@receiver(post_save, sender=Dimenzija)
def create_dimenzija(sender, instance, created, **kwargs):
    if created:
        sestavina = Sestavina.objects.create(dimenzija = instance)
        for prodaja in TIPI_PRODAJE:
            for tip in TIPI_SESTAVINE:
                Cena.objects.create(sestavina = sestavina, prodaja = prodaja[0], tip = tip[0])
    zacetna_stanja(sestavina.zaloga)
###################################################################################################

class Cena(models.Model):
    sestavina = models.ForeignKey(Sestavina, default=0, on_delete=models.CASCADE)
    cena = models.DecimalField(decimal_places=2,max_digits=5,default=0)
    tip = models.CharField(max_length=4, choices=TIPI_SESTAVINE, default="Y")
    prodaja = models.CharField(max_length=15, choices=TIPI_PRODAJE, default="vele_prodaja")
    


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
    skupna_cena = models.DecimalField(decimal_places=2,max_digits=6,default=0)
    skupno_stevilo = models.IntegerField(default = 0)

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
    def prodane(self):
        prodane = {}
        for racun in self.racuni:
            for vnos in racun.vnos_set.all():
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

    def __str__(self):
        return self.title
    
    def uveljavi_inventuro(self, datum = None, cas = None):
        self.status = "veljavno"
        self.doloci_cas(cas)
        self.doloci_datum(datum)
        spremembe = []
        for vnos in self.vnos_set.all().values():
            sestavina = Sestavina.objects.get(dimenzija_id = vnos['dimenzija_id'])
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

    def uveljavi_racun(self, cas = None):
        self.status = "veljavno"
        self.doloci_cas(cas)
        for vnos in self.vrni_vnose:
            sestavina = Sestavina.objects.get(dimenzija = vnos.dimenzija)
            sestavina.spremeni_stevilo(self.sprememba_zaloge * vnos.stevilo, vnos.tip)
            sprememba = Sprememba.objects.filter(baza__dnevna_prodaja = self.dnevna_prodaja, sestavina = sestavina, tip = vnos.tip ).first()
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
        dnevna_prodaja = self.dnevna_prodaja
        dnevna_prodaja.skupno_stevilo += self.skupno_stevilo
        dnevna_prodaja.skupna_cena += self.koncna_cena
        dnevna_prodaja.save()
        self.save()

    def uveljavi(self,datum=None,cas = None):
        self.status = "veljavno"
        self.doloci_cas(cas)
        self.doloci_datum(datum)
        for vnos in self.vnos_set.all():
            sestavina = Sestavina.objects.get(dimenzija = vnos.dimenzija)
            tip = vnos.tip
            sestavina.spremeni_stevilo(self.sprememba_zaloge * vnos.stevilo, vnos.tip)
            vnos.ustvari_spremembo(sestavina)

    def storniraj_racun(self):
        self.status = "storno"
        for vnos in self.vnos_set.all():
            sprememba = vnos.sprememba
            vnos.sprememba = None
            vnos.save()
            sestavina = sprememba.sestavina
            tip = sprememba.tip
            sprememba.stevilo_iz_vnosov()
            sestavina.nastavi_iz_sprememb(tip)
        dnevna_prodaja = self.dnevna_prodaja
        dnevna_prodaja.skupno_stevilo -= self.skupno_stevilo
        dnevna_prodaja.skupna_cena -= self.koncna_cena
        dnevna_prodaja.save()
        self.save()

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
                vnosi.update({dimenzija_tip: True})
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
            slovar = vnosi[vnos['dimenzija__dimenzija'] + '_' + vnos['tip']]
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
        cena = 0
        for vnos in self.vnos_set.all():
            cena += vnos.skupna_cena
        return cena

    @property
    def cena_popusta(self):
        return round(float(self.skupna_cena) * (self.popust / 100))

    @property
    def koncna_cena(self):
        return self.skupna_cena - self.cena_popusta

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

    def je_prazno(self):
        if self.vnos_set.all().count() == 0:
            return True
        
    def stevilo_iz_vnosov(self):
        stevilo = 0
        if self.je_prazno():
            self.delete()
        else:
            for vnos in self.vnos_set.all():
                stevilo += vnos.stevilo
            self.stevilo = stevilo
            self.save()

    def doloci_stevilo(self):
        stevilo = 0
        for vnos in self.vnos_set.all().values('stevilo'):
            stevilo += vnos['stevilo']
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
        return self.stevilo * self.cena

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
            sestavina = Sestavina.objects.get(dimenzija = self.dimenzija)
        self.sprememba = Sprememba.objects.create(
            baza = self.baza,
            stevilo = self.stevilo,
            tip = self.tip,
            sestavina = sestavina 
        )
        self.save()

class Stroski_Group(models.Model):
    title = models.CharField(default="",max_length=20)
    tip = models.CharField(default="",max_length=20)
    datum = models.DateField(default=timezone.now)
    status = models.CharField(default="aktivno",max_length=20)
    kontejner = models.ForeignKey(Kontejner,default=None,null=True,blank=True,on_delete=models.CASCADE)

class Strosek(models.Model):
    title = models.CharField(default="",max_length=20)
    group = models.ForeignKey(Stroski_Group,default=0,on_delete=models.CASCADE)
    delavec = models.ForeignKey(User,default=None,null=True,blank=True,on_delete=models.CASCADE)
    znesek = models.DecimalField(default=0,max_digits=8,decimal_places=2)
