from django.shortcuts import render
from django.db.models import Sum
from .models import Dimenzija, Sestavina, Vnos, Kontejner, Sprememba, Dnevna_prodaja, VnosZaloge, Dobavitelj
from .models import Baza, Zaloga, Cena
from django.shortcuts import redirect
from prodaja.models import Stranka
from django.db.models import Sum, OuterRef
from django.db.models.functions import Coalesce
import io
import datetime
from django.contrib.auth.decorators import login_required
import json
from . import funkcije
from request_funkcije import pokazi_stran, vrni_dimenzijo, vrni_slovar
from program.models import Program
from django.urls import reverse
from django.http import HttpResponse
from . import database_functions

#zaloga = Zaloga.objects.first()

##################################################################################################

@login_required
def pregled_zaloge(request,zaloga):
    if request.method == "GET":
        zaloga = Zaloga.objects.get(pk = zaloga)
        vnosi_zaloge = VnosZaloge.objects.filter(zaloga=zaloga)
        sestavine = vnosi_zaloge.all_values()
        if nicelne == "false":
            sestavine = sestavine.exclude(stanje=0)
        slovar = {
            'zaloga':zaloga,
            'sestavine':sestavine
        }
        return pokazi_stran(request, 'zaloga/zaloga.html', slovar)

@login_required
def pregled_prometa(request,tip,pk):
    if request.method == "GET":
        sestavina = Sestavina.objects.get(pk=pk)
        zaklep = sestavina.zaklep_zaloge
        cene_prodaje = Cena.objects.filter(sestavina=sestavina, prodaja__in = ['dnevna_prodaja','vele_prodaja'], tip=tip)
        danes = datetime.date.today().strftime('%Y-%m-%d')
        pred_mescem =  (datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        zacetek_sprememb = request.GET.get('zacetek_sprememb', pred_mescem)
        konec_sprememb = request.GET.get('konec_sprememb', danes)
        spremembe = sestavina.sprememba_set.filter(baza__datum__gt = zacetek_sprememb, baza__datum__lte=konec_sprememb, tip = tip).order_by('-baza__datum','-baza__cas').select_related('baza')
        zaporedna_stanja = sestavina.vrni_stanja(tip,zacetek_sprememb,konec_sprememb)[::-1]
        zacetek_dp = request.GET.get('zacetek_dp', pred_mescem)
        konec_dp = request.GET.get('konec_dp', danes)
        zacetek_vp = request.GET.get('zacetek_vp', pred_mescem)
        konec_vp = request.GET.get('konec_vp', danes)
        dp_stevilo, dp_cena = sestavina.prodaja('racun',tip, zacetek_dp, konec_dp)
        vp_stevilo, vp_cena = sestavina.prodaja('vele_prodaja',tip, zacetek_vp, konec_vp)
        slovar = {
            'zaporedna_stanja': zaporedna_stanja,
            'tip': tip,
            'sestavina': sestavina,
            'cene_prodaje':cene_prodaje,
            'spremembe': spremembe,
            'zacetek_sprememb': zacetek_sprememb,
            'zacetek_dp': zacetek_dp,
            'zacetek_vp': zacetek_vp,
            'konec_sprememb': konec_sprememb,
            'konec_dp': konec_dp,
            'konec_vp': konec_vp,
            'dp_stevilo': dp_stevilo,
            'dp_cena': dp_cena,
            'vp_stevilo': vp_stevilo,
            'vp_cena': vp_cena
        }
    return pokazi_stran(request, 'zaloga/pregled_prometa.html', slovar)

@login_required
def sprememba_cene(request,tip,pk,cena):
    if request.method=="POST":
        cena = Cena.objects.get(pk = cena )
        cena.cena = float(request.POST.get('cena'))
        cena.save()
    return redirect('pregled_prometa', tip=tip, pk=pk)

@login_required
def dodaj_dimenzijo(request):
    if request.method == "POST":
        dimenzija = request.POST.get('dimenzija')
        radius = request.POST.get('radius')
        height = request.POST.get('height')
        width = request.POST.get('width')
        special = request.POST.get('special')
        if special == "true":
            special = True
        elif special == "false":
            special = False
        Dimenzija.objects.create(
            dimenzija = dimenzija,
            radius = radius,
            height = height,
            width = width,
            special = special)
        return redirect('nova_dimenzija')
    else:
        return pokazi_stran(request, 'zaloga/dodaj_dimenzijo.html')

###############################################################################################################
###############################################################################################################
###############################################################################################################

@login_required
def baze(request,zaloga,tip_baze):
    if request.method == "GET":
        zaloga = Zaloga.objects.get(pk = zaloga)
        baze = Baza.objects.filter(zaloga = zaloga, tip=tip_baze,status='aktivno').all_values()
        stranke = Stranka.objects.all().order_by('stevilo_kupljenih').values('pk','naziv')
        zaloge = Zaloga.objects.all()
        skupno_stevilo = baze.aggregate(skupno = Sum("skupno_stevilo"))["skupno"]
        skupna_cena = baze.aggregate(cena = Sum("koncna_cena"))["cena"]
        skupen_ladijski_prevoz = baze.aggregate(skupno = Sum("ladijski_prevoz_value"))["skupno"]
        dobavitelji = None
        if tip_baze == "prevzem":
            dobavitelji = Dobavitelj.objects.all().all_values()
        slovar = {
            'zaloge':zaloge,
            'zaloga': zaloga,
            'tip': tip_baze,
            'baze':baze,
            'stranke':stranke,
            'skupno_stevilo':skupno_stevilo,
            'skupna_cena':skupna_cena,
            'skupen_ladijski_prevoz': skupen_ladijski_prevoz,
            'dobavitelji':dobavitelji
            }
        return pokazi_stran(request, 'zaloga/aktivne_baze.html', slovar)

@login_required
def nova_baza(request,zaloga,tip_baze):
    if request.method == "POST":
        program = Program.objects.first()
        if tip_baze == "narocilo":
            title = "narocilo"
        else:
            title = program.naslednja_baza(tip_baze,delaj = True)
        if tip_baze == "prevzem":
            stevilka = request.POST.get('stevilka')
            posiljatelj = request.POST.get('posiljatelj')
            drzava = request.POST.get('drzava')
            kontejner = Kontejner.objects.create(
                stevilka=stevilka,
                posiljatelj=posiljatelj,
                drzava=drzava)
            Baza.objects.create(
                zaloga_id = zaloga,
                title=title,
                kontejner=kontejner,
                author=request.user,
                tip=tip_baze,
                sprememba_zaloge = 1)
        elif tip_baze == "prenos":
            zalogaPrenosa = int(request.POST.get("zaloga"))
            Baza.objects.create(
                zaloga_id = zaloga,
                tip = tip_baze,
                sprememba_zaloge = -1,
                title = title,
                author = request.user,
                zalogaPrenosa = zalogaPrenosa
            )
        elif tip_baze == "vele_prodaja":
            stranka = Stranka.objects.get(pk = int(request.POST.get('stranka')))
            Baza.objects.create(
                zaloga_id = zaloga,
                stranka = stranka,
                title = title,
                popust = 0,
                prevoz = 0,
                placilo = 0,
                author = request.user,
                tip = tip_baze)
        elif tip_baze == 'inventura' or tip_baze == "odpis":
            Baza.objects.create(
                zaloga_id = zaloga,
                title=title,
                author=request.user,
                tip=tip_baze,
                sprememba_zaloge=0)
        return redirect('baze', zaloga=zaloga, tip_baze=tip_baze)

@login_required
def izbris_baze(request,zaloga, tip_baze, pk):
    if request.method == "POST":
        baza = Baza.objects.get(pk=pk)
        baza.delete()
        return redirect('baze', zaloga = zaloga, tip_baze=tip_baze) 

#######################################################################################################

def dolgovi(request, zaloga):
    if request.method == "GET":
        zaloga = Zaloga.objects.get(pk=zaloga)
        vele_prodaje = Baza.objects.filter(tip="vele_prodaja", status__in = ["veljavno", "zaklenjeno"])
        dolgovi = database_functions.baze_values(vele_prodaje).filter(placano=False)
        return pokazi_stran(request, 'dolgovi/dolgovi.html',{'dolgovi':dolgovi})
        
def poravnava_dolga(request, zaloga, baza):
    baza = Baza.objects.filter(pk=baza)
    baza_values = database_functions.baze_values(baza)[0]
    baza = baza.first()
    baza.placilo = baza_values["koncna_cena"]
    baza.save()
    return redirect("dolgovi", zaloga=zaloga)

#######################################################################################################

@login_required
def baza(request,zaloga, tip_baze, pk):
    if request.method == "GET":
        zaloga = Zaloga.objects.get(pk=zaloga)
        baza_query = Baza.objects.filter(pk = pk)
        baza = baza_query[0]
        baza_values = database_functions.baze_values(baza_query)[0]
        vnosi = Vnos.objects.filter(baza=baza,sestavina=OuterRef("id"))
        sestavine = zaloga.sestavine.all().all_values().vnosi_values(vnosi).zaloga_values(zaloga)
        dimenzije = Dimenzija.objects.all().values("dimenzija","id")
        slovar = {
            'zaloga': zaloga,
            'baza':baza,
            'tip':tip_baze,
            'status':baza.status,
            'dimenzije':dimenzije,
            'vnosi': baza.vnos_set.all().all_values(),
            'razlicni_radiusi': zaloga.vrni_razlicne_radiuse,
            'sestavine': sestavine,
            'tipi': zaloga.tipi_sestavin.all(),
            "values": baza_values}
        return pokazi_stran(request, 'baza/baza.html',slovar)
    

def poskus(request):
    print("tadej")
    return HttpResponse("TADEJ")

@login_required
def vnosi_iz_datoteke(request,zaloga,tip_baze, pk):
    zaloga = Zaloga.objects.get(pk=zaloga)
    seznam = funkcije.vnosi_iz_datoteke(request.FILES.get('datoteka'),zaloga)
    vnosi = []
    baza = Baza.objects.get(pk = pk)
    for vnos in seznam:
        sestavina = Sestavina.objects.get(tip__kratko=vnos["tip"],dimenzija_id=vnos['dimenzija_id'])
        v = Vnos(
            baza=baza,
            stevilo=vnos['stevilo'],
            sestavina = sestavina,
        )
        if tip_baze == "vele_prodaja":
            v.cena = zaloga.cenik.all().get(sestavina=sestavina).cena    
        vnosi.append(v)
    Vnos.objects.bulk_create(vnosi)
    return redirect('baza',zaloga=zaloga.pk, tip_baze = tip_baze, pk = pk)

def spremeni_placilo(request,zaloga, tip_baze, pk):
    if request.method=="POST":
        baza = Baza.objects.get(pk=pk)
        try:
            placilo = float(request.POST.get("placilo"))
            if not placilo > 0:
                placilo = 0
        except:
            placilo = 0
        baza.placilo = placilo
        baza.save()
        return redirect("baza",zaloga=zaloga,tip_baze=tip_baze,pk=pk)

def spremeni_ceno_nakupa(request,zaloga,tip_baze,pk):
    if request.method == "POST":
        baza = Baza.objects.get(pk = pk)
        try:
            cena = float(request.POST.get("cena_nakupa"))
            if not cena > 0:
                cena = 0
        except:
            cena = 0
        baza.cena = cena
        baza.save()
        return redirect("baza",zaloga=zaloga,tip_baze=tip_baze,pk=pk)

def nastavi_vnose_inventure(request,zaloga,tip_baze,pk):
    if request.method == "POST":
        baza = Baza.objects.get(pk = pk)
        baza.nastavi_vnose_inventure()
        return redirect("baza",zaloga=zaloga,tip_baze=tip_baze,pk=pk)

@login_required
def uveljavi_bazo(request,zaloga, tip_baze, pk):
    if request.method == "POST":
        baza = Baza.objects.get(pk = pk)
        if baza.status == "aktivno":
            baza.uveljavi()
    return redirect('arhiv_baz',zaloga=zaloga, tip_baze = tip_baze)

############################################################################################
############################################################################################
############################################################################################

@login_required
def arhiv(request,zaloga, tip_baze):
    if request.method == "GET":
        danes = datetime.date.today().strftime('%Y-%m-%d')
        pred_mescem =  (datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        zacetek = request.GET.get('zacetek', pred_mescem)
        konec = request.GET.get('konec', danes)
        zaloga = Zaloga.objects.get(pk =zaloga)
        stranke = Stranka.objects.all()
        stranka = None
        values = {}
        if tip_baze == "dnevna_prodaja":
            baze = Dnevna_prodaja.objects.filter(zaloga=zaloga,datum__gte=zacetek, datum__lte=konec).prefetch_related('baza_set').order_by('-datum')
            baze = database_functions.dnevne_prodaje_values(baze)
        else:
            baze = Baza.objects.filter(zaloga=zaloga,tip=tip_baze,status__in =['veljavno','zaklenjeno'],datum__gte=zacetek, datum__lte=konec).prefetch_related('vnos_set','stranka').order_by('-uveljavitev')
            stranka = request.GET.get('stranka','all')
            if tip_baze == "vele_prodaja" and stranka != "all":
                stranka = int(stranka)
                baze = baze.filter(stranka__id = stranka)
            baze = baze.all_values()
        try:
            values["stevilo_baz"] = baze.count()
            values["skupno_stevilo"] = baze.aggregate(stevilo=Coalesce(Sum("skupno_stevilo"),0))["stevilo"]
            values["skupna_cena"] = baze.aggregate(cena = Coalesce(Sum("koncna_cena"),0))["cena"]
            values["skupna_cena_nakupa"] = baze.aggregate(cena=Coalesce(Sum("skupna_cena_nakupa"),0))["cena"]
            values["skupen_zasluzek"] = baze.aggregate(cena=Coalesce(Sum("razlika"),0))["cena"]
            values["skupen_ladijski_prevoz"] = baze.aggregate(skupno=Sum("ladijski_prevoz_value"))["skupno"]
        except:
            print("NAPAKA")
            pass
        return pokazi_stran(request, 'arhiv_baz/arhiv_baz.html', {'zaloga': zaloga,'values':values, 'baze': baze, 'tip': tip_baze,'zacetek':zacetek,'konec':konec,'stranka':stranka,'stranke':stranke})
