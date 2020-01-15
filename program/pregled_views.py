from django.shortcuts import render
from zaloga.models import Zaloga, Dnevna_prodaja, Zaposleni
from prodaja.models import Stranka,Naslov
from django.contrib.auth.decorators import login_required
from prodaja.models import Prodaja
from django.shortcuts import redirect
from .models import Program
import json 
import datetime

@login_required
def pregled_zalog(request):
    if request.method == "GET":
        zaloge = Zaloga.objects.all()
        return pokazi_stran(request, 'pregled/pregled_zalog.html',{'zaloge':zaloge})

def pregled_zaloge(request, pk):
    zaloga = Zaloga.objects.get(pk = pk)
    slovar = {
        'zaloga':zaloga,
        'pk':pk
    }
    return pokazi_stran(request,'pregled/zaloga.html',slovar)

def sprememba_zaloge(request, pk):
    if request.method == "POST":
        title = request.POST.get('title')
        zaloga = Zaloga.objects.get(pk=pk)
        zaloga.title = title
        zaloga.save()
    return redirect('pregled_zaloge', pk=pk)

######################################################################

def pregled_zaposlenih(request):
    zaposleni = Zaposleni.objects.all()
    zaloge = Zaloga.objects.all()
    slovar = {
        'zaposleni':zaposleni,
        'zaloge':zaloge
    }
    return pokazi_stran(request,'pregled/pregled_zaposlenih.html',slovar)

def nov_zaposleni(request):
    if request.method == "POST":
        ime = request.POST.get('ime')
        priimek = request.POST.get('priimek')
        ime = request.POST.get('ime')
        davcna = request.POST.get('davcna')
        drzava = request.POST.get('drzava')
        mesto = request.POST.get('mesto')
        naslov = request.POST.get('naslov')
        naslov = Naslov.objects.create(drzava = drzava, mesto = mesto, naslov = naslov)
        telefon = request.POST.get('telefon')
        if davcna == "":
            davcna = "/"
        if telefon == "":
            telefon = "/"
        Zaposleni.objects.create(
            ime = ime,
            priimek = priimek,
            davcna = davcna,
            telefon = telefon,
            naslov = naslov)
    return redirect('pregled_zaposlenih')

def pregled_zaposlenega(request, pk):
    zaposleni = Zaposleni.objects.get(pk=pk)
    zaloge = Zaloga.objects.all()
    slovar={'zaposleni':zaposleni,'zaloge':zaloge}
    return pokazi_stran(request,'pregled/zaposleni.html',slovar)

def spremembna_zaposlenega(request, pk):
    if request.method=="POST":
        zaposleni = Zaposleni.objects.get(pk = pk)
        zaposleni.ime = request.POST.get('ime')
        zaposleni.priimek = request.POST.get('priimek')
        zaposleni.telefon = request.POST.get('telefon')
        #zaposleni.mail = request.POST.get('mail')
        zaposleni.davcna = request.POST.get('davcna')
        zaposleni.naslov.drzava = request.POST.get('drzava')
        zaposleni.naslov.mesto = request.POST.get('mesto')
        zaposleni.naslov.naslov = request.POST.get('naslov')
        zaposleni.save()
    return redirect('ogled_zaposlenega', pk = pk)

###############################################################################################

def pregled_strank(request):
    stranke = Stranka.objects.all().filter(status = 'aktivno').order_by('skupna_cena_kupljenih')
    return pokazi_stran(request, 'pregled/pregled_strank.html', {'stranke': stranke})

def izbris_stranke(request, pk):
    stranka = Stranka.objects.get(pk = pk)
    stranka.izbrisi()
    return redirect('pregled_strank')

def ogled_stranke(request, pk):
    stranka = Stranka.objects.get(pk=pk)
    return pokazi_stran(request,'pregled/stranka.html',{'stranka':stranka})

def spremembna_stranke(request, pk):
    if request.method=="POST":
        stranka = Stranka.objects.get(pk = pk)
        stranka.ime = request.POST.get('ime')
        stranka.naziv = request.POST.get('naziv')
        stranka.telefon = request.POST.get('telefon')
        stranka.mail = request.POST.get('mail')
        stranka.davcna = request.POST.get('davcna')
        stranka.naslov.drzava = request.POST.get('drzava')
        stranka.naslov.mesto = request.POST.get('mesto')
        stranka.naslov.naslov = request.POST.get('naslov')
        stranka.save()
    return redirect('ogled_stranke', pk = pk)

def nova_stranka(request):
    naziv = request.POST.get('naziv')
    ime = request.POST.get('ime')
    davcna = request.POST.get('davcna')
    drzava = request.POST.get('drzava')
    mesto = request.POST.get('mesto')
    naslov = request.POST.get('naslov')
    naslov = Naslov.objects.create(drzava = drzava, mesto = mesto, naslov = naslov)
    telefon = request.POST.get('telefon')
    mail = request.POST.get('mail')
    if mail == "":
        mail = "/"
    if davcna == "":
        davcna = "/"
    if telefon == "":
        telefon = "/"
    Stranka.objects.create(
        naziv = naziv,
        ime = ime,
        davcna = davcna,
        telefon = telefon,
        mail = mail,
        naslov = naslov)
    return redirect('pregled_strank')

###############################################################################################
###############################################################################################

def vrni_slovar(request):
    with open('slovar.json') as dat:
        slovar = json.load(dat)
    return slovar

def pokazi_stran(request, html, baze={}):
    slovar = {'slovar':vrni_slovar(request),'jezik':request.user.profil.jezik}
    slovar.update(baze)
    if not 'zaloga' in baze:
        slovar.update({'zaloga':Zaloga.objects.first()})
    slovar.update({'zaloga_pk':slovar['zaloga'].pk})
    return render(request, html, slovar)