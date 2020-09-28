from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from zaloga.models import Dimenzija,Sestavina, Zaloga
from prodaja.models import Stranka
from datetime import datetime

JEZIKI = (
    ('slo','Slovenscina'),
    ('ang','Anglescina'),
    ('spa', 'Spanscina'),
)

class Program(models.Model):
    stevilo_prevzemov = models.IntegerField(default = 0)
    stevilo_odpisov = models.IntegerField(default = 0)
    stevilo_faktur = models.IntegerField(default = 0)
    stevilo_racunov = models.IntegerField(default = 0)
    stevilo_inventur = models.IntegerField(default = 0)
    stevilo_prenosov = models.IntegerField(default = 0)

    def naslednja_baza(self,tip,delaj=False):
        if tip == "prevzem":
            return self.naslednji_prevzem(delaj)
        elif tip == "odpis":
            return self.naslednji_odpis(delaj)
        elif tip == "racun":
            return self.naslednji_racun(delaj)
        elif tip == "vele_prodaja":
            return self.naslednja_faktura(delaj)
        elif tip == "inventura":
            return self.naslednja_inventura(delaj)
        elif tip == "prenos":
            return self.naslednji_prenos(delaj)
                
    def naslednja_faktura(self,delaj=False):
        if delaj:
            self.stevilo_faktur += 1
            self.save()
            return str(self.stevilo_faktur) + '/2020'
        else:
            return str(self.stevilo_faktur + 1) + '/2020'
        
    def naslednji_racun(self,delaj=False):
        if delaj:
            self.stevilo_racunov += 1
            self.save()
            for n in range(1,6):
                if self.stevilo_racunov // (10 ** (5-n)) != 0:
                    return '0' * n + str(self.stevilo_racunov)
        else:
            for n in range(1,6):
                if (self.stevilo_racunov + 1) // (10 ** (5-n)) != 0:
                    return '0' * n + str(self.stevilo_racunov + 1)
    
    def naslednji_prevzem(self,delaj=False):
        if delaj:
            self.stevilo_prevzemov += 1
            self.save()
            return 'P-2020-' + str(self.stevilo_prevzemov)
        else:
            return 'P-2020-' + str(self.stevilo_prevzemov + 1)
        
    def naslednji_odpis(self,delaj=False):
        if delaj:
            self.stevilo_odpisov += 1
            self.save()
            return 'O-2020-' + str(self.stevilo_odpisov)
        else:
            return 'O-2020-' + str(self.stevilo_odpisov + 1)

    def naslednji_prenos(self,delaj=False):
        if delaj:
            self.stevilo_prenosov += 1
            self.save()
            return 'PS-2020-' + str(self.stevilo_prenosov)
        else:
            return 'PS-2020-' + str(self.stevilo_prenosov + 1)


    def naslednja_inventura(self,delaj=False):
        if delaj:
            self.stevilo_inventur += 1
            self.save()
            return 'I-2020-' + str(self.stevilo_inventur)
        else:
            return 'I-2020-' + str(self.stevilo_inventur + 1)
        
    @property
    def vrni_jezike(self):
        return JEZIKI

    @property
    def danes(self):
        return datetime.today().strftime('%Y-%m-%d')

    
    def vrni_slovar_dimenzij(self, obratno = False):
        slovar = {}
        dimenzije = Sestavina.objects.all().values('dimenzija_id','dimenzija__dimenzija')
        if obratno:
            for dimenzija in dimenzije:
                slovar.update({dimenzija['dimenzija_id']:dimenzija['dimenzija__dimenzija']})
        else: 
            for dimenzija in dimenzije:
                slovar.update({dimenzija['dimenzija__dimenzija']:dimenzija['dimenzija_id']})
        return slovar

    def vrni_dimenzijo(self,radius,height,width):
        special = False
        if "C" in width:
            special = True
            width = width[:-1]
        return Dimenzija.objects.get(radius = radius,height=height,width=width,special=special)

    @property
    def vrni_dimenzije(self):
        return Dimenzija.objects.all().values_list('dimenzija','radius','height','width','special')

class Profil(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    jezik =  models.CharField(default="spa",max_length=3, choices=JEZIKI)
    aktivna_zaloga = models.ForeignKey(Zaloga, default=1, on_delete=models.CASCADE)
    dovoljene_zaloge = models.ManyToManyField(Zaloga, related_name = "dovoljene")
    stranka = models.OneToOneField(Stranka, on_delete=models.CASCADE, default=None, null=True, blank=True)
    celo_ime = models.CharField(default="",max_length=40)
    tip_banke = models.CharField(default="",max_length=40)
    stevilka_racuna = models.CharField(default="",max_length=40)
    telefon = models.CharField(default="",max_length=40)
    
    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profil.objects.create(user = instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profil.save()

