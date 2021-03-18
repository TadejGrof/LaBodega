from django.shortcuts import render

from django.http import JsonResponse
from zaloga.models import Dimenzija
from django.db.models import F

def dimenzije(request):
    dimenzije = list(Dimenzija.objects.all().values()\
    .annotate(radij=F("radius"))\
    .annotate(sirina=F("height"))\
    .annotate(visina=F("width"))\
    .annotate(special=F("special"))\
    .values("id","radij","sirina","visina","special"))
    return JsonResponse(dimenzije,safe=False)
