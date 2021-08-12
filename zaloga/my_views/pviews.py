from django.shortcuts import render
from zaloga.models import Vnos, Zaloga, Dimenzija, Sestavina, Baza, Cena, Dnevna_prodaja
from django.shortcuts import redirect
import datetime
from django.utils import timezone
from program.models import Program
import json 
from request_funkcije import vrni_dimenzijo, vrni_slovar, pokazi_stran
from django.urls import reverse

def dnevna_prodaja(request,zaloga,dnevna_prodaja):
    zaloga = Zaloga.objects.get(pk=zaloga)
    prodaja = Dnevna_prodaja.objects.get(id=dnevna_prodaja)
    aktivni_racun = prodaja.aktivni_racun
    return pokazi_stran(request, 'prodaja/dnevna_prodaja.html', {'prodaja': prodaja, 'aktivni_racun': aktivni_racun})

def nova_dnevna_prodaja(request,zaloga):
    if request.method == "POST":
        zaloga = Zaloga.objects.get(pk = zaloga)
        dnevna_prodaja = Dnevna_prodaja.objects.create(zaloga = zaloga)
    return redirect('dnevna_prodaja',zaloga=zaloga.pk)

###########################################################################################

def uveljavi_racun(request,zaloga,pk_racuna):
    if request.method == "POST":
        zaloga = Zaloga.objects.get(pk = zaloga)
        program = Program.objects.first()
        racun = Baza.objects.get(pk = pk_racuna)
        racun.uveljavi()
        racun.dnevna_prodaja.nov_racun()
        danes = timezone.localtime(timezone.now())
        danes = datetime.datetime(danes.year,danes.month,danes.day).date()
        if danes == racun.dnevna_prodaja.datum:
            return redirect('dnevna_prodaja',zaloga=zaloga.pk)
        else:
            return redirect('ogled_dnevne_prodaje',zaloga=zaloga.pk, pk_prodaje = racun.dnevna_prodaja.pk)

def storniraj_racun(request,zaloga,pk_prodaje,pk_racuna):
    racun = Baza.objects.get(pk = pk_r)
    racun.storniraj_racun()
    return redirect('ogled_dnevne_prodaje', zaloga = zaloga, pk = pk)

def ogled_racuna(request,zaloga, pk_racuna):
    racun = Racun.objects.get(pk = pk)
    return pokazi_stran(request, 'prodaja/ogled_racuna.html', {'racun':racun})

def nastavi_praznik(request,zaloga, dnevna_prodaja):
    prodaja = Dnevna_prodaja.objects.get(pk=dnevna_prodaja)
    prodaja.tip = "Praznik"
    prodaja.save()
    return redirect("arhiv_baz",zaloga=zaloga, tip_baze="dnevna_prodaja")

def dodaj_dnevne_prodaje(request,zaloga):
    zacetek_str = request.POST.get('zacetek')
    konec_str = request.POST.get('konec')
    zacetek = datetime.datetime.strptime(zacetek_str,'%Y-%m-%d')
    konec = datetime.datetime.strptime(konec_str,'%Y-%m-%d')
    zaloga = Zaloga.objects.get(pk=zaloga)
    prodaje = Dnevna_prodaja.objects.all().filter(zaloga=zaloga,datum__lte=konec, datum__gte=zacetek)
    datum = zacetek
    while datum <= konec:
        if not prodaje.filter(datum=datum).exists():
            Dnevna_prodaja.objects.create(zaloga=zaloga, datum=datum)
        datum += datetime.timedelta(days=1)
    url = reverse('arhiv_baz', args=[zaloga.pk,"dnevna_prodaja"])
    url += "?zacetek=" + zacetek_str + "&konec=" + konec_str
    print(url)
    return redirect(url)

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
    
