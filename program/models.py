from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.

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
                
    def naslednja_faktura(self,delaj=False):
        if delaj:
            self.stevilo_faktur += 1
            self.save()
            return str(self.stevilo_faktur) + '/2019'
        else:
            return str(self.stevilo_faktur + 1) + '/2019'
        
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
            return 'P-2019-' + str(self.stevilo_prevzemov)
        else:
            return 'P-2019-' + str(self.stevilo_prevzemov + 1)
        
    def naslednji_odpis(self,delaj=False):
        if delaj:
            self.stevilo_odpisov += 1
            self.save()
            return 'O-2019-' + str(self.stevilo_odpisov)
        else:
            return 'O-2019-' + str(self.stevilo_odpisov + 1)
        
    def naslednja_inventura(self,delaj=False):
        if delaj:
            self.stevilo_inventur += 1
            self.save()
            return 'I-2019-' + str(self.stevilo_inventur)
        else:
            return 'I-2019-' + str(self.stevilo_inventur + 1)
        
    @property
    def vrni_jezike(self):
        return JEZIKI

class Profil(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    jezik =  models.CharField(default="spa",max_length=3, choices=JEZIKI)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profil.objects.create(User = instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profil.save()