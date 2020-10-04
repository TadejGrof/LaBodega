from django.shortcuts import render
from zaloga.models import Zaloga, Dnevna_prodaja, Baza
from django.contrib.auth.decorators import login_required
from prodaja.models import Prodaja
from django.shortcuts import redirect
from .models import Program
import json 
import datetime
from request_funkcije import pokazi_stran, vrni_slovar

@login_required
def ponastavi_zalogo(request):
    zaloga = Zaloga.objects.first()
    zaloga.ponastavi_zalogo()
    return redirect('pregled_zaloge')

@login_required
def home_page(request):
    zaloga = request.user.profil.aktivna_zaloga
    prodaja = Prodaja.objects.first()
    stranke = prodaja.stranka_set.all().filter(status="aktivno").prefetch_related('baza_set').values(
        "pk",
        "naziv",
        "telefon",
        "mail"
    )
    prodaje = Baza.objects.all().filter(zaloga = zaloga, status="aktivno", tip="vele_prodaja").values(
        "stranka",
        "pk"
    )
    for stranka in stranke:
        for prodaja in prodaje:
            if prodaja["stranka"] == stranka["pk"]:
                stranka["aktivna_prodaja"] = True
                stranka["aktivna_prodaja__pk"] = prodaja["pk"]
                break
            stranka["aktivna_prodaja"] = False
    #for stranka in stranke.iterator():
    #    print(stranka.aktivna_prodaja)

    tip = request.GET.get('tip','all')
    radius = request.GET.get('radius','all')
    if tip == "all":
        sestavine = zaloga.vrni_top_10(radius)
    elif radius == "all":
        sestavine = zaloga.sestavina_set.all().order_by('-' + tip)[:10].values('dimenzija__dimenzija',tip)
        for sestavina in sestavine:
            sestavina.update({'tip':tip})
    else:
        sestavine = zaloga.sestavina_set.all().filter(dimenzija__radius = radius).order_by('-' + tip)[:10].values('dimenzija__dimenzija',tip)
        for sestavina in sestavine:
            sestavina.update({'tip':tip})
    danasnja_prodaja = Dnevna_prodaja.objects.filter(zaloga = zaloga, datum = datetime.date.today()).first()
    slovar = {
        'dnevna_prodaja':danasnja_prodaja,
        'stranke':stranke,
        'sestavine':sestavine,
        'tip':tip,
        'zaloga':zaloga,
        'zaloga_pk': zaloga.pk,
        }
    return pokazi_stran(request, 'program/home_page.html', slovar)

@login_required
def profil(request):
    stranka = request.user.profil.stranka
    je_stranka = True if stranka != None else False
    return pokazi_stran(request,'program/profil.html',{'je_stranka':je_stranka,'stranka':stranka})

@login_required
def spremeni_jezik(request):
    if request.method == "POST":
        jezik = request.POST.get('jezik')
        request.user.profil.jezik = jezik
        request.user.save()
        return redirect('home_page')

@login_required
def spremeni_zalogo(request, pk):
    if request.method == "POST":
        zaloga = Zaloga.objects.get(pk = pk)
        request.user.profil.aktivna_zaloga = zaloga
        request.user.save()
        return redirect('home_page')