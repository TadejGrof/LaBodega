from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation
from datetime import datetime
from django.contrib.auth.models import User
import datetime

class Prodaja(models.Model):
    title = models.CharField(default='prodaja',max_length=30)
    stevilo_faktur = models.IntegerField(default=0)
    stevilo_racunov = models.IntegerField(default=0)
    
    def naslednja_faktura(self):
        self.stevilo_faktur += 1
        self.save()
        return str(self.stevilo_faktur) + '/2019'
        
    @property
    def vrni_naslednjo_fakturo(self):
        return str(self.stevilo_faktur) + '/2019'
    
    def naslednji_racun(self):
        self.stevilo_racunov += 1
        self.save()
        for n in range(1,6):
            if self.stevilo_racunov // (10 ** (5-n)) != 0:
                return '0' * n + str(self.stevilo_racunov)

    @property
    def danes(self):
        return datetime.today().strftime('%Y-%m-%d')

    @property
    def stranke(self):
        return self.stranka_set.all().values('pk','ime','telefon','mail')

#poskus
class Naslov(models.Model):
    drzava = models.CharField(default="", max_length=20)
    mesto = models.CharField(default="", max_length=20)
    naslov = models.CharField(default="", max_length=40)

class Skupina(models.Model):
    naziv = models.CharField(default="", max_length=30)

    def __str__(self):
        return self.naziv

class Stranka(models.Model):
    prodaja = models.ForeignKey(Prodaja, default=1, on_delete=models.CASCADE)
    naziv = models.CharField(default="", max_length=30)
    ime = models.CharField(default="", max_length=30)
    telefon = models.CharField(default="", max_length=20)
    mail = models.CharField(default="",max_length=40)
    naslov = models.OneToOneField(Naslov, on_delete=models.CASCADE, default=0)
    davcna = models.CharField(default="", max_length=30)
    status = models.CharField(default='aktivno',max_length=10)
    stevilo_kupljenih = models.IntegerField(default=0)
    skupna_cena_kupljenih = models.DecimalField(decimal_places=1,max_digits=5,default=0)
    skupina = models.ForeignKey(Skupina,default=None,null=True,blank=True,on_delete=models.SET_NULL)

    def __str__(self):
        return self.ime
        
    @property
    def ima_aktivno_prodajo(self):
        return self.baza_set.all().filter(status="aktivno").exists()

    def ima_aktivno_prodajo(self,zaloga):
        return self.baza_set.all().filter(zaloga=zaloga,status="aktivno").exists()

    @property
    def aktivna_prodaja(self):
        return self.baza_set.all().filter(status="aktivno").first()
