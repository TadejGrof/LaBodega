from django.shortcuts import render
from ..models import Dimenzija, Sestavina, Vnos, Kontejner, Dnevna_prodaja, Tip, VnosZaloge
from ..models import Baza, Zaloga, Cena
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import json 
from .. import funkcije
from request_funkcije import pokazi_stran, vrni_slovar
from request_funkcije import vrni_dimenzijo as dimenzija_iz_requesta
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_POST,require_GET
from django.apps import apps


@require_POST
def save(request):
    model = apps.get_model("zaloga",request.POST.get("class_name"))
    data = json.loads(request.POST.get("attributes"))
    object = model.objects.get(id = data["id"])
    print(data)
    for attr in data:
        try:
            if "__" in attr:
                seznam = attr.split("__")
                parent = object
                while len(seznam) > 1:
                    parent = getattr(parent,seznam.pop(0))
                setattr(parent,seznam[0],data[attr])
                parent.save()
            setattr(object,attr,data[attr])
        except:
            continue
    object.save()
    parent = None
    if request.POST.get("hasParent","false") == "true":
        parent = getattr(object,request.POST.get("parentAttr"))
    data = {
        "success":True,
        "model":object.all_values(),
        "parent": parent.all_values() if parent != None else {},
    }
    return JsonResponse(data)

@require_POST
def create(request):
    model = apps.get_model("zaloga",request.POST.get("class_name"))
    print(str(request.POST))
    print(request.POST.get("attributes"))
    data = json.loads(request.POST.get("attributes"))
    object = model()
    print(data)
    for attr in data:
        try:
            setattr(object,attr,data[attr])
        except:
            continue
    object.save()
    parent = None
    if request.POST.get("hasParent","false") == "true":
        parent = getattr(object,request.POST.get("parentAttr"))
    data = {
        "success":True,
        "model":object.all_values(),
        "parent": parent.all_values() if parent != None else {},
    }
    return JsonResponse(data)

@require_POST
def delete(request):
    model = apps.get_model("zaloga",request.POST.get("class_name"))
    data = json.loads(request.POST.get("attributes"))
    object = model.objects.get(id=data["id"])
    parent = None
    if request.POST.get("hasParent","false") == "true":
        parent = getattr(object,request.POST.get("parentAttr"))
    object.delete()
    data = {
        "success":True,
        "parent": parent.all_values() if parent != None else {},
    }
    return JsonResponse(data)
