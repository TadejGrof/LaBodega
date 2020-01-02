from django.shortcuts import render
from .models import Dimenzija, Sestavina, Vnos, Kontejner, Sprememba, Dnevna_prodaja
from .models import Baza, Zaloga, Cena
from django.shortcuts import redirect
from prodaja.models import Prodaja, Stranka
import io
import datetime
from django.contrib.auth.decorators import login_required
import json 
from program.models import Program
from . import funkcije

prodaja = Prodaja.objects.first()
zaloga = Zaloga.objects.first()
program = Program.objects.first()


##################################################################################################

@login_required
def pregled_zaloge(request):
    if request.method == "GET":
        sestavine = zaloga.sestavina_set.all()
        radius = request.GET.get('radius','R12')
        height = request.GET.get('height','all')
        width = request.GET.get('width', 'all')
        nicelne = request.GET.get('nicelne','true')
        cenik = zaloga.cenik('vele_prodaja')
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
        tipi = []
        for tip in zaloga.vrni_tipe:
            if request.GET.get(tip[0],"true") == "true":
                tipi.append(tip)
        sestavine = sestavine.values(
            'dimenzija__dimenzija',
            'pk',
            'Y',
            'W',
            'JP',
            'JP50',
            'JP70',
        )
        if nicelne == "false":
            ne_prazne = []
            for sestavina in sestavine:
                for tip in tipi:
                    if sestavina[tip[0]] != 0:
                        ne_prazne.append(sestavina)
                        break
            sestavine = ne_prazne
        cene = {}
        skupno = 0
        vrednost = 0
        for sestavina in sestavine:
            dimenzija = sestavina['dimenzija__dimenzija']
            for tip in tipi:
                stevilo = sestavina[tip[0]]
                cena = cenik[dimenzija][tip[0]]
                skupno += stevilo
                vrednost += cena * stevilo
                if dimenzija in cene:
                    if not tip[0] in cene[dimenzija]:
                        cene[dimenzija].update({tip[0]:stevilo * cena})
                else:
                    cene.update({dimenzija:{tip[0]:stevilo * cena}})
        slovar = {
            'sestavine':sestavine,
            'tipi':tipi,
            'radius':radius,
            'height':height,
            'width':width,
            'skupno':skupno,
            'nicelne': nicelne,
            'cene':cene,
            'vrednost':vrednost
        }
        return pokazi_stran(request, 'zaloga/zaloga.html', slovar)

@login_required
def pregled_prometa(request):
    if request.method == "GET":
        pk = request.GET.get('pk', Sestavina.objects.first().pk)
        tip = request.GET.get('tip', zaloga.vrni_tipe[0][0])
        sestavina = Sestavina.objects.get(pk=pk)
        spremembe = sestavina.sprememba_set.filter(tip = tip).order_by('-baza__datum','-baza__cas').select_related('baza')
        zaporedna_stanja = sestavina.vrni_stanja(tip)[::-1]
        cene_prodaje = Cena.objects.filter(sestavina=sestavina, prodaja__in = ['dnevna_prodaja','vele_prodaja'], tip=tip)
        danes = datetime.date.today().strftime('%Y-%m-%d')
        pred_mescem =  (datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        zacetek_sprememb = request.GET.get('zacetek_sprememb', pred_mescem)
        konec_sprememb = request.GET.get('konec_sprememb', danes)
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
        print(slovar)
    return pokazi_stran(request, 'zaloga/pregled_prometa.html', slovar)

@login_required
def sprememba_cene(request, pk):
    if request.method=="POST":
        cena = Cena.objects.get(pk = pk )
        cena.cena = float(request.POST.get('cena'))
        cena.save()
    return redirect('pregled_prometa')

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
        return redirect('pregled_zaloge')
    else:
        return pokazi_stran(request, 'zaloga/dodaj_dimenzijo.html')

@login_required
def sestavine_iz_datoteke(request):
    seznam = dodaj_sestavine_iz_datoteke(request.FILES.get('datoteka'))
    for dimenzija in seznam:
        dim = Dimenzija.objects.create(dimenzija = dimenzija['dimenzija'],radius=dimenzija['radius'],width=dimenzija['width'],height=dimenzija['height'],special=dimenzija['special'])
        Sestavina.objects.create(dimenzija=dim, zaloga=zaloga)
    return redirect('pregled_zaloge')

###############################################################################################################
###############################################################################################################
###############################################################################################################

@login_required
def baze(request, tip_baze):
    if request.method == "GET":
        baze = Baza.objects.filter(tip=tip_baze,status='aktivno')
        stranke = Stranka.objects.all().order_by('stevilo_kupljenih').values('pk','naziv')
        return pokazi_stran(request, 'zaloga/aktivne_baze.html', {'tip': tip_baze, 'baze':baze,'stranke':stranke})
        
@login_required
def nova_baza(request, tip_baze):
    if request.method == "POST":
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
                title=title,
                kontejner=kontejner,
                author=request.user,
                tip=tip_baze,
                sprememba_zaloge = 1)
        elif tip_baze == "vele_prodaja" or tip_baze == "narocilo":
            stranka = Stranka.objects.get(pk = int(request.POST.get('stranka')))
            Baza.objects.create(
                stranka = stranka,
                title = title,
                popust = 0,
                prevoz = 0,
                author = request.user,
                tip = tip_baze)
        elif tip_baze == 'inventura' or tip_baze == "odpis":
            Baza.objects.create(
                title=title,
                author=request.user,
                tip=tip_baze)
        return redirect('baze', tip_baze=tip_baze)

@login_required
def izbris_baze(request, tip_baze, pk):
    if request.method == "POST":
        baza = Baza.objects.get(pk=pk)
        baza.delete()
        return redirect('baze', tip_baze=tip_baze)

#######################################################################################################

@login_required
def baza(request, tip_baze, pk):
    if request.method == "GET":
        baza = Baza.objects.get(pk = pk)
        if baza.status == "aktivno":
            slovar = {
                'baza':baza,
                'vnosi':baza.inventurni_vnosi,
                'tip':tip_baze,
                'status':"aktivno",
                'na_voljo':zaloga.na_voljo,
                'razlicni_radiusi':zaloga.vrni_razlicne_radiuse,
                'sestavine':zaloga.vrni_zalogo,
                'tipi': zaloga.vrni_tipe}
            return pokazi_stran(request, 'zaloga/baza.html',slovar)
        elif baza.status == "veljavno":
            return pokazi_stran(request, 'zaloga/baza.html',{'baza':baza,'tip':tip_baze, 'status':"veljavno"})
        elif baza.status == "zaklenjeno":
            return pokazi_stran(request, 'zaloga/baza.html',{'baza':baza,'tip':tip_baze, 'status':"zaklenjeno"})   

@login_required
def nov_vnos(request, tip_baze, pk):
    if request.method == "POST":
        dimenzija = vrni_dimenzijo(request)
        stevilo = request.POST.get('stevilo')
        tip = request.POST.get('tip')
        baza = Baza.objects.get(pk = pk)
        if tip_baze == "vele_prodaja":
            vnos = Vnos.objects.create(
                dimenzija = dimenzija,
                stevilo = stevilo,
                tip = tip,
                cena = Sestavina.objects.get(dimenzija=dimenzija).cena('vele_prodaja',tip),
                baza = baza)
        else:
            vnos = Vnos.objects.create(
                dimenzija = dimenzija,
                stevilo = stevilo,
                tip = tip,
                baza = baza)
        if baza.status == "veljavno":
            sestavina = Sestavina.objects.get(dimenzija = vnos.dimenzija)
            vnos.ustvari_spremembo(sestavina)
            sestavina.nastavi_iz_sprememb(vnos.tip)
        return redirect('baza', tip_baze = tip_baze, pk = pk)

@login_required
def shrani_vse(request,tip_baze, pk):
    if request.method == "POST":
        baza = Baza.objects.get(pk = pk)
        vnosi = []
        for sestavina in zaloga.vrni_zalogo:
            for tip in zaloga.vrni_tipe:
                stevilo = request.POST.get(sestavina['dimenzija'] + '_' + tip[0])
                if stevilo != "":
                    dimenzija = Dimenzija.objects.get(dimenzija = sestavina['dimenzija'])
                    if tip_baze == "vele_prodaja":
                        vnosi.append(Vnos(
                            dimenzija = dimenzija,
                            tip = tip[0],
                            stevilo = stevilo,
                            cena = Sestavina.objects.get(dimenzija = dimenzija).cena("vele_prodaja",tip[0]),
                            baza = baza))
                    else: 
                        vnosi.append(Vnos(
                            dimenzija = dimenzija,
                            tip = tip[0],
                            stevilo = stevilo,
                            baza = baza))
        Vnos.objects.bulk_create(vnosi)
        return redirect('baza', tip_baze=tip_baze, pk = pk)   

@login_required
def vnosi_iz_datoteke(request, tip_baze, pk):
    seznam = funkcije.vnosi_iz_datoteke(request.FILES.get('datoteka'),zaloga)
    vnosi = []
    baza = Baza.objects.get(pk = pk)
    if tip_baze == "vele_prodaja":
        for vnos in seznam:
            sestavina = Sestavina.objects.get(dimenzija_id=vnos['dimenzija_id'])
            vnosi.append(Vnos(
                    baza=baza,
                    stevilo=vnos['stevilo'],
                    tip=vnos['tip'],
                    dimenzija_id=vnos['dimenzija_id'],
                    cena=sestavina.cena('vele_prodaja',vnos['tip'])
                ))
    else:
        for vnos in seznam:
            vnosi.append(Vnos(
                baza=baza,
                stevilo=vnos['stevilo'],
                tip=vnos['tip'],
                dimenzija_id=vnos['dimenzija_id']
            ))
    Vnos.objects.bulk_create(vnosi)
    return redirect('baza', tip_baze = tip_baze, pk = pk)

@login_required
def spremeni_vnos(request, tip_baze, pk):
    if request.method == "POST":
        stevilo = request.POST.get('stevilo')
        cena = request.POST.get('cena')
        tip = request.POST.get('tip')
        vnos = Vnos.objects.get(pk = request.POST.get('pk'))
        if stevilo and stevilo != "":
            vnos.stevilo = int(request.POST.get('stevilo'))
        if tip:
            vnos.tip = request.POST.get('tip')
        if cena and cena != "" :
            vnos.cena = float(request.POST.get('cena'))
        if tip_baze == "inventura":
            vnos.inventurna_sprememba(stevilo)
        vnos.save()
        return redirect('baza', tip_baze = tip_baze, pk = pk)

@login_required
def izbrisi_vnos(request, tip_baze, pk):
    if request.method == "POST":
        vnos = Vnos.objects.get(pk = request.POST.get('pk'))
        baza = Baza.objects.get(pk = pk)
        if baza.status == "veljavno":
            if tip_baze == "inventura":
                vnos.inventurni_izbris()
            else:
                tip = vnos.tip
                sestavina = Sestavina.objects.get(dimenzija = vnos.dimenzija)
                vnos.sprememba.delete()
                sestavina.nastavi_iz_sprememb(tip)
        elif baza.status == "aktivno":
            vnos.delete()
        return redirect('baza', tip_baze=tip_baze, pk = pk)

@login_required
def spremeni_popust(request,tip_baze, pk):
    if request.method == "POST":
        prodaja = Baza.objects.get(pk = pk)
        prodaja.popust = request.POST.get('popust')
        prodaja.save()
        return redirect('baza',tip_baze=tip_baze,pk=pk)

@login_required
def spremeni_prevoz(request,tip_baze, pk):
    if request.method == "POST":
        prodaja = Baza.objects.get(pk = pk)
        prodaja.prevoz = request.POST.get('prevoz')
        prodaja.save()
        return redirect('baza',tip_baze=tip_baze,pk=pk)

@login_required
def uveljavi_bazo(request, tip_baze, pk):
    if request.method == "POST":
        baza = Baza.objects.get(pk = pk)
        if baza.status == "aktivno":
            if tip_baze == 'inventura':
                baza.uveljavi_inventuro()
            else:
                baza.uveljavi()
    return redirect('arhiv_baz', tip_baze = tip_baze)

############################################################################################
############################################################################################
############################################################################################

@login_required
def arhiv(request, tip_baze):
    if request.method == "GET":
        danes = datetime.date.today().strftime('%Y-%m-%d')
        pred_mescem =  (datetime.date.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        zacetek = request.GET.get('zacetek', pred_mescem)
        konec = request.GET.get('konec', danes)
        stranke = Stranka.objects.all()
        stranka = None
        if tip_baze == "dnevna_prodaja":
            baze = Dnevna_prodaja.objects.filter(datum__gte=zacetek, datum__lte=konec).prefetch_related('baza_set').order_by('-datum')
        else:
            baze = Baza.objects.filter(tip=tip_baze,status='veljavno',datum__gte=zacetek, datum__lte=konec).prefetch_related('vnos_set','stranka').order_by('-datum','-cas')
            stranka = request.GET.get('stranka','all')
            if tip_baze == "vele_prodaja" and stranka != "all":
                stranka = int(stranka)
                baze = baze.filter(stranka__id = stranka)
        return pokazi_stran(request, 'zaloga/arhiv_baz.html', {'baze': baze, 'tip': tip_baze,'zacetek':zacetek,'konec':konec,'stranka':stranka,'stranke':stranke})

###################################################################################
###################################################################################
###################################################################################

def vrni_dimenzijo(request):
    if request.POST.get('dimenzija'):
        return Dimenzija.objects.get(dimenzija=request.POST.get('dimenzija'))
    else:
        radius = request.POST.get('radius')
        height = request.POST.get('height')
        width = request.POST.get('width')
        special = False
        if 'C' in width:
            width = width.replace('C','')
            special = True
        return Dimenzija.objects.get(radius=radius,height=height,width=width,special=special)

def vrni_slovar(request):
    with open('slovar.json') as dat:
        slovar = json.load(dat)
    return slovar

def pokazi_stran(request, html, baze={}):
    slovar = {'prodaja':prodaja, 'zaloga':zaloga,'program':program,'slovar':vrni_slovar(request),'jezik':request.user.profil.jezik}
    slovar.update(baze)
    return render(request, html, slovar)