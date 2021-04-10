from django.shortcuts import render

from django.http import JsonResponse, HttpResponse
from zaloga.models import Dimenzija
from django.db.models import F
from django.contrib.auth import authenticate as auth
from django.contrib.auth.models import User
from django.middleware.csrf import get_token

def authenticate(request):
    json= {"authanticated":False}
    if request.method == "POST":
        username = request.POST.get("username","")
        password = request.POST.get("password","")
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