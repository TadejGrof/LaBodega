from django.shortcuts import render
from .models import Kontejner, Stroski_Group, Strosek, Zaposleni
from .models import Baza, Zaloga, Dnevna_prodaja
from django.shortcuts import redirect
import datetime
from django.contrib.auth.decorators import login_required
import json 
from django.contrib.auth.models import User
from request_funkcije import pokazi_stran, vrni_slovar


@login_required
def pregled_narocil(request):
    stranka = request.user.profil.stranka
    if stranka != None:
        narocila = stranka.baza_set.all().filter( status__in = ["aktivno","pregledano","na_poti"])
        return pokazi_stran(request,'stranka/pregled.html', {'stranka':stranka,'narocila':narocila})
    else:
        return redirect('home_page')

@login_required
def novo_narocilo(request):
    pass

@login_required
def ogled_narocila(request, pk):
    pass

@login_required
def zgodovina(request):
    stranka = request.user.profil.stranka
    if stranka != None:
        danes = datetime.date.today().strftime('%Y-%m-%d')
        pred_pol_leta =  (datetime.date.today() - datetime.timedelta(days=180)).strftime('%Y-%m-%d')
        zacetek = request.GET.get('zacetek', pred_pol_leta)
        konec = request.GET.get('konec', danes)
        baze = Baza.objects.filter(stranka = stranka, status='aktivno',datum__gte=zacetek, datum__lte=konec).prefetch_related('vnos_set','stranka').order_by('-datum','-cas')
        slovar = {
            'baze': baze,
            'zacetek':zacetek,
            'konec':konec,
            'stranka':stranka
        }
    return pokazi_stran(request, 'stranka/zgodovina.html',slovar)