from django.shortcuts import render
from .models import Kontejner, Stroski_Group, Strosek, Zaposleni
from .models import Baza, Zaloga, Dnevna_prodaja
from django.shortcuts import redirect
import datetime
from django.contrib.auth.decorators import login_required
import json 
from django.contrib.auth.models import User
from django.shortcuts import render
from request_funkcije import vrni_slovar, pokazi_stran

zaloga = Zaloga.objects.all().first()

@login_required
def pregled(request):
    danes = datetime.date.today().strftime('%Y-%m-%d')
    pred_mescem =  (datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    od = request.GET.get('od',pred_mescem)
    do = request.GET.get('do', danes)
    stroski = Stroski_Group.objects.all().filter(datum__gte = od, datum__lte = do).order_by('-datum','-pk').prefetch_related('strosek_set')
    pod_stroski = []
    for strosek in stroski:
        pod_stroski.append(strosek.strosek_set.all().values())
    skupno = 0
    for strosek in stroski:
        skupno += strosek.skupni_znesek
    slovar = {
        'od':od,
        'do':do,
        'stroski':stroski,
        'skupno':skupno,
        'pod_stroski':pod_stroski,
    }
    return pokazi_stran(request,'stroski/pregled_stroskov.html',slovar)

@login_required
def strosek(request):
    strosek = Stroski_Group.objects.all().filter(status = 'aktivno').first()
    kontejnerji = Kontejner.objects.all().order_by('-baza__datum')[:10].values('stevilka','pk')
    vnosi = strosek.strosek_set.all() if strosek != None else None
    zaposleni = Zaposleni.objects.all()
    return pokazi_stran(request,'stroski/nov_strosek.html',{'strosek':strosek,'kontejnerji':kontejnerji,'vnosi':vnosi,'zaposleni':zaposleni})

@login_required
def nov_strosek(request):
    if request.method == "POST":
        title = request.POST.get('title')
        tip = request.POST.get('tip')
        datum = request.POST.get('datum')
        kontejner = None
        if tip == "kontejner":
            kontejner = Kontejner.objects.get(pk = int(request.POST.get('kontejner')))
        Stroski_Group.objects.create(
            title = title,
            tip = tip,
            datum = datum,
            kontejner = kontejner
        )
    return redirect('strosek')

@login_required
def izbris_vnosa(request, pk , pk_vnosa):
    if request.method == "POST":
        Strosek.objects.get(pk = pk_vnosa).delete()
    return redirect('strosek')

@login_required
def uveljavi(request,pk):
    if request.method == "POST":
        strosek = Stroski_Group.objects.get(pk = pk)
        strosek.status = "veljavno"
        strosek.save()
    return redirect('pregled_stroskov')

@login_required
def nov_vnos(request, pk):
    if request.method == "POST":
        strosek = Stroski_Group.objects.get(pk = pk)
        delavec = None
        title = request.POST.get('tip')
        if strosek.tip == "placa":
            delavec = Zaposleni.objects.get(pk = int(request.POST.get('delavec')))
            title = delavec.ime
        Strosek.objects.create(
            group = strosek,
            delavec = delavec,
            title = title,
            znesek = float(request.POST.get('znesek'))
        )
        return redirect('strosek')

###################################################################################
###################################################################################

def porocilo_prometa(request):
    danes = datetime.date.today().strftime('%Y-%m-%d')
    pred_mescem =  (datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    od = request.GET.get('od',pred_mescem)
    do = request.GET.get('do', danes)
    stroski = Stroski_Group.objects.all().filter(datum__gte = od, datum__lte = do).order_by('-datum','-pk').prefetch_related('strosek_set')
    vele_prodaje = Baza.objects.all().filter(tip="vele_prodaja",datum__gte=od,datum__lte=do,status="veljavno").order_by('-datum','-pk').prefetch_related('vnos_set')
    dnevne_prodaje = Dnevna_prodaja.objects.all().filter(datum__gte=od,datum__lte=do).order_by('-datum','-pk')
    promet = []
    for strosek in stroski.iterator():
        slovar = {
            'tip':'Strosek',
            'znesek':-float(strosek.skupni_znesek),
            'title':strosek.title,
            'datum':strosek.datum,
        }
        promet.append(slovar)
    for vele_prodaja in vele_prodaje.iterator():
        slovar = {
            'tip':'Vele prodaja',
            'znesek':float(vele_prodaja.koncna_cena),
            'title':vele_prodaja.title,
            'datum':vele_prodaja.datum,
        }
        promet.append(slovar)
    for dnevna_prodaja in dnevne_prodaje.iterator():
        slovar = {
            'tip':'Dnevna prodaja',
            'znesek':float(dnevna_prodaja.skupna_cena),
            'title':dnevna_prodaja.title,
            'datum':dnevna_prodaja.datum,
        }
        promet.append(slovar)
    promet = sorted(promet,key = lambda i: (i['datum'],i['tip'],i['znesek']), reverse=True)
    pretok, skupno = pregled_prometa(promet)
    slovar = {
        'pretok':pretok,
        'skupno':skupno,
        'promet':promet,
        'od':od,
        'do':do,
    }
    return pokazi_stran(request,'porocilo/porocilo.html',slovar)

def porocilo_prodaje(request):
    danes = datetime.date.today().strftime('%Y-%m-%d')
    pred_mescem =  (datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    od = request.GET.get('od',pred_mescem)
    do = request.GET.get('do', danes)
    vele_prodaje = Baza.objects.all().filter(tip="vele_prodaja",datum__gte=od,datum__lte=do,status="veljavno").order_by('-datum','-pk').prefetch_related('vnos_set')
    dnevne_prodaje = Dnevna_prodaja.objects.all().filter(datum__gte=od,datum__lte=do).order_by('-datum','-pk')
    sestavine = {}
    skupno = {tip:{'skupno':0,'vele_prodaja':0,'dnevna_prodaja':0} for tip in ['stevilo','cena']}
    for prodaja in vele_prodaje.iterator():
        for vnos in prodaja.vnos_set.all().values('dimenzija__dimenzija','tip','stevilo','cena'):
            dimenzija = vnos['dimenzija__dimenzija']
            stevilo = vnos['stevilo']
            cena = float(vnos['cena'])
            tip = vnos['tip']
            ime = dimenzija + '-' + tip
            if ime in sestavine:
                    sestavine[ime]['stevilo'] += stevilo
                    sestavine[ime]['cena'] += stevilo * cena 
                    sestavine[ime]['stevilo_vele_prodaje'] += stevilo
                    sestavine[ime]['cena_vele_prodaje'] += stevilo * cena
            else:
                slovar = {ime:{
                        'stevilo':stevilo,
                        'cena':cena*stevilo,
                        'stevilo_dnevne_prodaje':0,
                        'cena_dnevne_prodaje':0,
                        'cena_vele_prodaje':cena*stevilo,
                        'stevilo_vele_prodaje':stevilo}}
                sestavine.update(slovar)
            for skupno_tip in ['skupno','vele_prodaja']:
                skupno['stevilo'][skupno_tip] += stevilo
                skupno['cena'][skupno_tip] += stevilo * cena
    for prodaja in dnevne_prodaje.iterator():
        for racun in prodaja.baza_set.all().filter(status="veljavno").prefetch_related('vnos_set'):
            for vnos in racun.vnos_set.all().values('dimenzija__dimenzija','tip','stevilo','cena'):
                dimenzija = vnos['dimenzija__dimenzija']
                stevilo = vnos['stevilo']
                cena = float(vnos['cena'])
                tip = vnos['tip']
                ime = dimenzija + '-' + tip
                if ime in sestavine:
                        sestavine[ime]['stevilo'] += stevilo
                        sestavine[ime]['cena'] += stevilo * cena
                        sestavine[ime]['stevilo_dnevne_prodaje'] += stevilo
                        sestavine[ime]['cena_dnevne_prodaje'] += stevilo * cena 
                else:
                    slovar = {ime:{
                        'stevilo':stevilo,
                        'cena':cena*stevilo,
                        'stevilo_dnevne_prodaje':stevilo,
                        'cena_dnevne_prodaje':cena*stevilo,
                        'cena_vele_prodaje':0,
                        'stevilo_vele_prodaje':0}}
                    sestavine.update(slovar)
                for skupno_tip in ['skupno','dnevna_prodaja']:
                    skupno['stevilo'][skupno_tip] += stevilo
                    skupno['cena'][skupno_tip] += stevilo * cena
    sestavine = sorted(sestavine.items(),key=lambda x: (x[1]['stevilo'],x[1]['cena']),reverse=True)
    slovar = {
        'sestavine':sestavine,
        'skupno':skupno,
        'od':od,
        'do':do,
    }
    
    return pokazi_stran(request,'porocilo/porocilo_prodaje.html', slovar)
###################################################################################
###################################################################################
###################################################################################

def pregled_prometa(promet):
    cene, skupno = [], 0
    for sprememba in promet:
        skupno += sprememba['znesek']
        cene.append(skupno)
    return cene, skupno