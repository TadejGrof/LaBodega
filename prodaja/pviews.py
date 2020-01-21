from django.shortcuts import render
from .models import Stranka, Prodaja, Naslov
from zaloga.models import Vnos, Zaloga, Dimenzija, Sestavina, Baza, Cena, Dnevna_prodaja
from django.shortcuts import redirect
import datetime
from django.utils import timezone
from program.models import Program
import json 
from request_funkcije import vrni_dimenzijo, vrni_slovar, pokazi_stran

program = Program.objects.first()
prodaja = Prodaja.objects.first()
zaloga = Zaloga.objects.first()


# Create your views here.
def pregled_prodaje(request):
    pass

###########################################################################################
###########################################################################################
###########################################################################################

def dnevna_prodaja(request):
    danes = timezone.localtime(timezone.now())
    danasnja_prodaja = Dnevna_prodaja.objects.filter(datum = danes).first()
    aktivni_racun = None
    na_voljo = zaloga.na_voljo
    if danasnja_prodaja != None:
        aktivni_racun = danasnja_prodaja.aktivni_racun
    return pokazi_stran(request, 'prodaja/dnevna_prodaja.html', {'prodaja': danasnja_prodaja, 'aktivni_racun': aktivni_racun,'na_voljo':na_voljo})

def nova_dnevna_prodaja(request):
    if request.method == "POST":
        dnevna_prodaja = Dnevna_prodaja.objects.create()
        dnevna_prodaja.doloci_title()
        Baza.objects.create(
            title = program.naslednji_racun(delaj=True),
            tip='racun',
            dnevna_prodaja = dnevna_prodaja,
            popust = 0 )
    return redirect('dnevna_prodaja')

###########################################################################################

def nov_racun(request):
    if request.method == "POST":
        prodaja = Dnevna_prodaja.objects.filter(datum = datetime.date.today()).first()
        Baza.objects.create(
            title= program.naslednji_racun(delaj=True),
            tip='racun',
            dnevna_prodaja = prodaja,
            popust = 0,)
    return redirect('dnevna_prodaja')

def racun_nov_vnos(request, pk):
    if request.method == "POST":
        racun = Baza.objects.get(pk = pk)
        dimenzija = vrni_dimenzijo(request)
        stevilo = request.POST.get('stevilo')
        tip = request.POST.get('tip')
        cena = Sestavina.objects.get(dimenzija = dimenzija).cena('dnevna_prodaja', tip)
        vnos = Vnos.objects.create(dimenzija = dimenzija, cena = cena, stevilo = stevilo, tip = tip, baza = racun)
    return redirect('dnevna_prodaja')

def racun_sprememba_vnosa(request):
    if request.method == "POST":
        vnos = Vnos.objects.get(pk = request.POST.get('pk'))
        stevilo = request.POST.get('stevilo')
        if stevilo != "":
            vnos.stevilo = stevilo
        cena = request.POST.get('cena')
        if cena != "":
            vnos.cena = float(cena)
        vnos.tip = request.POST.get('tip')
        vnos.save()
    return redirect('dnevna_prodaja')

def racun_izbris_vnosa(request):
    if request.method == "POST":
        Vnos.objects.get(pk = request.POST.get('pk')).delete()
    return redirect('dnevna_prodaja')

def racun_spremeni_popust(request):
    if request.method == "POST":
        racun = Baza.objects.get(pk = request.POST.get('pk'))
        racun.popust = request.POST.get('popust')
        racun.save()
    return redirect('dnevna_prodaja')

def uveljavi_racun(request,pk):
    if request.method == "POST":
        racun = Baza.objects.get(pk = pk)
        racun.uveljavi_racun()
        Baza.objects.create(
            title = program.naslednji_racun(delaj=True),
            tip = 'racun',
            dnevna_prodaja = racun.dnevna_prodaja,
            popust = 0,)
    return redirect('dnevna_prodaja')

###########################################################################################

def ogled_dnevne_prodaje(request, pk):
    prodaja = Dnevna_prodaja.objects.get(pk = pk)
    if prodaja.stevilo_veljavnih_racunov() > 0:
        racun_pk = request.GET.get('racun_pk', prodaja.baza_set.filter(tip='racun', status='veljavno').last().pk)
        racun = Baza.objects.get(pk = racun_pk)
    else:
        racun = None
    racuni = prodaja.baza_set.all().filter(tip='racun', status__in = ['veljavno','storno']).order_by('-pk').prefetch_related('vnos_set')
    return pokazi_stran(request,'prodaja/ogled_dnevne_prodaje.html',{'prodaja':prodaja, 'racuni': racuni, 'racun': racun})

def storniraj_racun(request,pk,pk_r):
    racun = Baza.objects.get(pk = pk_r)
    racun.storniraj_racun()
    return redirect('ogled_dnevne_prodaje', pk = pk)

def ogled_racuna(request, pk):
    racun = Racun.objects.get(pk = pk)
    return pokazi_stran(request, 'prodaja/ogled_racuna.html', {'racun':racun})

###########################################################################################
###########################################################################################
###########################################################################################    

def cenik(request,baza):
    if request.method == "GET":
        sestavine = zaloga.sestavina_set.all()
        radius = request.GET.get('radius','R12')
        height = request.GET.get('height','all')
        width = request.GET.get('width','all')
        if radius != "all":
            sestavine = sestavine.filter(dimenzija__radius=radius)
        if height != "all":
            sestavine = sestavine.filter(dimenzija__height=height)
        if width != "all":
            if "C" in width:
                width = width.replace('C','')
                sestavine = sestavine.filter(dimenzija__width=width, dimenzija__special = True)
            else:
                sestavine = sestavine.filter(dimenzija__width=width, dimenzija__special = False)
        sestavine = sestavine.prefetch_related('cena_set').filter(cena__prodaja=baza).values(
            'dimenzija__dimenzija',
            'pk',
            'cena',
            'cena__tip',
            'cena__cena')
        tipi = []
        for tip in zaloga.vrni_tipe:
            if request.GET.get(tip[0],"true") == "true":
                tipi.append(tip[0])
        slovar = {
            'sestavine':sestavine,
            'tip':baza,
            'tipi':tipi,
            'radius':radius,
            'height':height,
            'width':width}
    return pokazi_stran(request,'prodaja/cenik.html', slovar)

def spremeni_ceno(request, baza):
    nova_cena = float(request.POST.get('cena'))
    pk = int(request.POST.get('pk'))
    cena = Cena.objects.get(pk = pk)
    cena.cena = nova_cena
    cena.save()
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
    
