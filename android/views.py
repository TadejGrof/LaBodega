from django.shortcuts import render

from django.http import JsonResponse, HttpResponse
from zaloga.models import Dimenzija
from django.db.models import F
from django.contrib.auth import authenticate as auth
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def authenticate(request):
    json= {"authenticated":False}
    if request.method == "POST":
        print(request.POST)
        username = request.POST.get("username","")
        password = request.POST.get("password","")
        print(request.POST)
        user = auth(username=username,password=password)
        json["username"] = username
        json["password"] = password
        if user is not None:
            json["authenticated"] = True
    return JsonResponse(json,safe=False)

def dimenzije(request):
    dimenzije = list(Dimenzija.objects.all().values()\
    .annotate(radij=F("radius"))\
    .annotate(sirina=F("height"))\
    .annotate(visina=F("width"))\
    .annotate(special=F("special"))\
    .values("id","radij","sirina","visina","special"))
    return JsonResponse(dimenzije,safe=False)

def get_csrf(request):
    csrf = get_token(request)
    return HttpResponse(csrf)

def cenik(request):
    zaloga = Zaloga.objects.first()
    tip_prodaje = "vele_prodaja"
    nacin = "prodaja"
    cenik = Cena.objects.all().filter(sestavina__zaloga = zaloga, prodaja=tip_prodaje, nacin = nacin).values("cena","tip").annotate(dimenzija = F("sestavina__dimenzija__dimenzija"))
    cenik_json = {}
    for cena in cenik:
        dimenzija = cena["dimenzija"]
        tip = cena["tip"]
        if dimenzija in cenik_json:
            cenik_json[dimenzija][tip] = cena["cena"]
        else:
            cenik_json[dimenzija] = {tip:cena["cena"]}
    print(cenik_json)