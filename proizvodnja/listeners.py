from .models import * 
from django.db.models.signals import post_save, pre_save, post_delete
from django.db.models.functions import Concat, Cast
from django.db.models import F, CharField, Value
from django.dispatch import receiver

@receiver(post_save, sender=Zaloga)
def create_zaloga(sender, instance, created, **kwargs):
    if created:
        print("CREATED ZALOGA")
        print("ADDING VNOSI ZALOGE")
        vnosi_zaloge = []
        for sestavina in Sestavina.objects.all():
            vnosi_zaloge.append(VnosZaloge(
                zaloga = instance,
                sestavina = sestavina
            ))
        VnosZaloge.objects.bulk_create(vnosi_zaloge)

@receiver(post_save, sender=Sestavina)
def create_sestavina(sender, instance, created, **kwargs):
    if created:
        print("CREATED SESTAVINA")
        print("ADDING VNOSI ZALOGE")
        vnosi_zaloge = []
        for zaloga in Zaloga.objects.all():
            vnosi_zaloge.append(VnosZaloge(
                zaloga = zaloga,
                sestavina = instance
            ))
        VnosZaloge.objects.bulk_create(vnosi_zaloge)