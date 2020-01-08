from django.shortcuts import render
from zaloga.models import Zaloga, Dnevna_prodaja
from django.contrib.auth.decorators import login_required
from prodaja.models import Prodaja
from django.shortcuts import redirect
from .models import Program
import json 
import datetime

zaloga = Zaloga.objects.first()
prodaja = Prodaja.objects.first()
program = Program.objects.first()

@login_required
def ponastavi_zalogo(request):
    zaloga.ponastavi_zalogo()
    return redirect('pregled_zaloge')

@login_required
def home_page(request):
    stranke = prodaja.stranka_set.all().filter(status="aktivno")
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
    danasnja_prodaja = Dnevna_prodaja.objects.filter(datum = datetime.date.today()).first()
    slovar = {
        'dnevna_prodaja':danasnja_prodaja,
        'stranke':stranke,
        'sestavine':sestavine,
        'tip':tip,
        }
    return pokazi_stran(request, 'program/home_page.html', slovar)

@login_required
def spremeni_jezik(request):
    if request.method == "POST":
        jezik = request.POST.get('jezik')
        request.user.profil.jezik = jezik
        request.user.save()
        return redirect('home_page')



##########################################################################################
##########################################################################################
##########################################################################################

def vrni_slovar(request):
    with open('slovar.json') as dat:
        slovar = json.load(dat)
    return slovar

def pokazi_stran(request, html, baze={}):
    slovar = {'prodaja':prodaja,'program':program,'slovar':vrni_slovar(request),'jezik':request.user.profil.jezik}
    slovar.update(baze)
    if not 'zaloga' in baze:
        slovar.update({'zaloga':zaloga})
    slovar.update({'zaloga_pk':slovar['zaloga'].pk})
    return render(request, html, slovar)