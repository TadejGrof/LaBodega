from pickle import FALSE
from django.shortcuts import render
from prodaja.models import Stranka, Prodaja, Naslov
from zaloga.models import Vnos, Zaloga, Dimenzija, Sestavina, Baza, Cena, Dnevna_prodaja
from django.shortcuts import redirect
import datetime
from django.utils import timezone
from program.models import Program
import json
from request_funkcije import vrni_dimenzijo, vrni_slovar, pokazi_stran
from django.http import HttpResponse, JsonResponse
from zaloga.funkcije import filtriraj_dimenzije
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required

def json_dnevne_prodaje(request, zaloga, dnevna_prodaja):
    return JsonResponse(Dnevna_prodaja.objects.get(pk=dnevna_prodaja).json,safe=False)

def dnevna_prodaja(request,zaloga):
    zaloga = Zaloga.objects.get(pk=zaloga)
    danes = timezone.localtime(timezone.now())
    danasnja_prodaja = Dnevna_prodaja.objects.filter(datum = danes).first()
    aktivni_racun = None
    na_voljo = zaloga.na_voljo
    if danasnja_prodaja != None:
        aktivni_racun = danasnja_prodaja.aktivni_racun
    return pokazi_stran(request, 'prodaja/dnevna_prodaja.html', {'danasnja':True,'prodaja': danasnja_prodaja, 'aktivni_racun': aktivni_racun,'na_voljo':na_voljo})

def nova_dnevna_prodaja(request,zaloga):
    if request.method == "POST" or request.method == "GET":
        print(zaloga)
        zaloga = Zaloga.objects.get(pk = zaloga)
        program = Program.objects.first()
        dnevna_prodaja = Dnevna_prodaja.objects.create(zaloga = zaloga)
        dnevna_prodaja.doloci_title()
        Baza.objects.create(
            zaloga = zaloga,
            title = program.naslednji_racun(delaj=True),
            tip='racun',
            dnevna_prodaja = dnevna_prodaja,
            popust = 0 )
    return redirect('dnevna_prodaja',zaloga=zaloga.pk)

###########################################################################################

def nov_racun(request,zaloga):
    if request.method == "POST":
        zaloga = Zaloga.objects.get(pk = pk)
        program = Program.objects.first()
        prodaja = Dnevna_prodaja.objects.filter(datum = datetime.date.today()).first()
        Baza.objects.create(
            zaloga = zaloga,
            author=request.user,
            title= program.naslednji_racun(delaj=True),
            tip='racun',
            dnevna_prodaja = prodaja,
            popust = 0,)
    return redirect('dnevna_prodaja',zaloga = zaloga.pk)

def uveljavi_racun(request,zaloga,pk_racuna):
    if request.method == "POST":
        zaloga = Zaloga.objects.get(pk = zaloga)
        program = Program.objects.first()
        racun = Baza.objects.get(pk = pk_racuna)
        racun.uveljavi()
        Baza.objects.create(
            zaloga = zaloga,
            title = program.naslednji_racun(delaj=True),
            tip = 'racun',
            datum = racun.dnevna_prodaja.datum,
            dnevna_prodaja = racun.dnevna_prodaja,
            popust = 0)
        danes = timezone.localtime(timezone.now())
        danes = datetime.datetime(danes.year,danes.month,danes.day).date()
        if danes == racun.dnevna_prodaja.datum:
            return redirect('dnevna_prodaja',zaloga=zaloga.pk)
        else:
            return redirect('ogled_dnevne_prodaje',zaloga=zaloga.pk, pk_prodaje = racun.dnevna_prodaja.pk)

###########################################################################################

def ogled_dnevne_prodaje(request,zaloga, pk_prodaje):
    zaloga = Zaloga.objects.get(pk=zaloga)
    na_voljo = zaloga.na_voljo
    prodaja = Dnevna_prodaja.objects.get(pk = pk_prodaje)
    aktivni_racun = prodaja.aktivni_racun
    return pokazi_stran(request, 'prodaja/dnevna_prodaja.html', {'danasnja':False,'prodaja': prodaja, 'aktivni_racun': aktivni_racun,'na_voljo':na_voljo})

def storniraj_racun(request,zaloga,pk_prodaje,pk_racuna):
    racun = Baza.objects.get(pk = pk_r)
    racun.storniraj_racun()
    return redirect('ogled_dnevne_prodaje', zaloga = zaloga, pk = pk)

def ogled_racuna(request,zaloga, pk_racuna):
    racun = Racun.objects.get(pk = pk)
    return pokazi_stran(request, 'prodaja/ogled_racuna.html', {'racun':racun})


###########################################################################################

@login_required
def pregled_prometa(request,zaloga):
    do_datum = datetime.date.today().strftime('%Y-%m-%d')
    od_datum =  (datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    return pokazi_stran(request, 'prodaja/pregled_prodaje.html', {'od': od_datum, "do": do_datum})

@login_required
def pregled_prodaje(request,zaloga):
    od_datum = request.GET.get("od",datetime.date.today())
    do_datum = request.GET.get("do",datetime.date.today() - datetime.timedelta(days=30))
    dimenzija_filter = request.GET.get("dimenzija")
    dimenzije = filtriraj_dimenzije(dimenzija_filter)
    vnosi = Vnos.objects.filter(dimenzija__in = [d["id"] for d in dimenzije],baza__zaloga=zaloga, baza__tip="racun", baza__status="veljavno", baza__dnevna_prodaja__datum__gte = od_datum, baza__dnevna_prodaja__datum__lte = do_datum).values(
        "dimenzija__dimenzija", "stevilo", "tip","cena"
    )
    sestevek = sestevek_vnosov(vnosi)
    vnosi = []
    zaloga = Zaloga.objects.get(id=zaloga)
    skupno_stevilo = 0
    skupna_cena = 0
    for dimenzija in dimenzije:
        for tip in ["Y","W","JP70"]:
            dimenzija_tip = dimenzija["dimenzija"] + "_" + tip
            if dimenzija_tip in sestevek:
                vnosi.append(
                    {
                        "dimenzija": dimenzija["dimenzija"],
                        "tip": tip,
                        "stevilo": sestevek[dimenzija_tip]["stevilo"],
                        "cena": float(sestevek[dimenzija_tip]["cena"])
                    }
                )
                skupno_stevilo += sestevek[dimenzija_tip]["stevilo"]
                skupna_cena += sestevek[dimenzija_tip]["cena"]

    data = {"html": render_to_string("prodaja/tabela_prodanih.html",{"vnosi":vnosi,"skupno_stevilo":skupno_stevilo,"skupna_cena":skupna_cena})}
    print(vnosi)
    print(data)
    print(skupno_stevilo)
    print(skupna_cena)
    return JsonResponse(data,safe=False)

def sestevek_vnosov(vnosi):
    slovar = {}
    for vnos in vnosi:
        dimenzija_tip = vnos["dimenzija__dimenzija"] + "_" + vnos["tip"]
        if dimenzija_tip in slovar:
            slovar[dimenzija_tip]["stevilo"] += vnos["stevilo"]
            slovar[dimenzija_tip]["cena"] += vnos["stevilo"] * vnos["cena"] if vnos["cena"] else 0
        else:
            slovar[dimenzija_tip] = {
                "stevilo": vnos["stevilo"],
                "cena": vnos["cena"] * vnos["stevilo"] if vnos["cena"] else 0
            }
    return slovar

 ###########################################################################################
###########################################################################################
###########################################################################################

def cenik(request,baza,zaloga):
    if request.method == "GET":
        zaloga = Zaloga.objects.get(pk = zaloga)
        sestavine = zaloga.sestavina_set.all()
        sestavine = sestavine.prefetch_related('cena_set').filter(cena__prodaja=baza).values(
            'dimenzija__dimenzija',
            'dimenzija__radius',
            'dimenzija__height',
            'dimenzija__width',
            'dimenzija__special',
            'pk',
            'cena',
            'cena__tip',
            'cena__cena',
            'cena__pk')
        slovar = {
            'sestavine':sestavine,
            'tip':baza,
        }
    return pokazi_stran(request,'prodaja/cenik.html', slovar)

def spremeni_ceno(request, baza):
    try:
        nova_cena = float(request.POST.get('cena'))
        pk = int(request.POST.get('pk'))
        cena = Cena.objects.get(pk = pk)
        cena.cena = nova_cena
        cena.save()
        data = {}
        data['cena'] = str(cena.cena)
    except:
        pass
    return redirect('cenik_prodaje', baza=baza)

def spremeni_cene(request,baza):
    if request.method == "POST":
        for cena in Cena.objects.filter(prodaja=baza).all():
            nova_cena = request.POST.get('cena_' + str(cena.pk))
            if nova_cena and nova_cena != '':
                nova_cena = float(nova_cena)
                cena.cena = nova_cena
                cena.save()
    return redirect('cenik_prodaje', baza=baza)

###########################################################################################
###########################################################################################
###########################################################################################

def porocilo(request):
    danes = datetime.date.today().strftime('%Y-%m-%d')
    pred_mescem =  (datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    zacetek = request.GET.get('zacetek', pred_mescem)
    konec = request.GET.get('konec', danes)

