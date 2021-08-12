from django.shortcuts import render
from zaloga.models import Zaloga, Dnevna_prodaja, Baza
from django.contrib.auth.decorators import login_required
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
    zaloga = Zaloga.objects.get(id=request.user.profil.aktivna_zaloga)
    

    danasnja_prodaja = Dnevna_prodaja.objects.filter(zaloga = zaloga, datum = datetime.date.today()).first()
    slovar = {
        'dnevna_prodaja':danasnja_prodaja,
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
        request.user.profil.aktivna_zaloga = pk
        request.user.save()
        return redirect('home_page')