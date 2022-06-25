from django.shortcuts import render

from zaloga.funkcije import analiza_narocil
from ..models import Dimenzija, Sestavina, Vnos, Dnevna_prodaja
from ..models import Baza, Zaloga
from ..models import Kontejner, Stroski_Group, Strosek, Zaposleni
from django.shortcuts import redirect
import zaloga.pdf as pdf
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
import datetime
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from django.http import HttpResponse
from zaloga.funkcije import analiza_narocil


#zaloga = Zaloga.objects.first()

def pdf_zaloge(request,zaloga):
    zaloga = Zaloga.objects.get(pk = zaloga)
    radius = request.GET.get('radius')
    sestavine = zaloga.sestavina_set.all()
    nicelne = request.GET.get('nicelne','true')
    rezervirane = request.GET.get('rezervirane','false')
    print(rezervirane)
    na_voljo = zaloga.na_voljo
    if radius != 'all':
        sestavine = zaloga.sestavina_set.all().filter(dimenzija__radius = radius)
    tipi = []
    for tip in zaloga.vrni_tipe:
        if request.GET.get(tip[0]):
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
    if rezervirane == "true":
        for sestavina in sestavine:
            for tip in tipi:
                dimenzija_tip = sestavina['dimenzija__dimenzija'] + "_" + tip[0]
                sestavina[tip[0]] = na_voljo[dimenzija_tip]
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="zaloga.pdf"'
    
    p = canvas.Canvas(response)
    p.translate(40,800)
    p.drawString(200,0,'Pregled zaloge')
    pdf.tabela_zaloge(p,zaloga,sestavine,tipi)
    p.showPage()
    p.save()
    return response 
    
def pdf_cenika(request,zaloga,tip_prodaje):
    radius = request.GET.get('radius',"all")
    zaloga = Zaloga.objects.get(pk=zaloga)
    sestavine = zaloga.sestavina_set.all()
    print(sestavine)
    print(radius)
    print(radius == "")
    if radius != 'all' and radius != "":
        sestavine = sestavine.filter(dimenzija__radius = radius)
    tipi = []
    for tip in zaloga.vrni_tipe:
        if request.GET.get(tip[0]):
            tipi.append(tip)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="cenik.pdf"'
    p = canvas.Canvas(response)

    p.translate(40,800)
    if tip_prodaje == "vele_prodaja":
        p.drawString(200,0,'Cenik vele prodaje')
    elif tip_prodaje == "dnevna_prodaja":
        p.drawString(200,0,'Cenik dnevne prodaje')
    pdf.cenik(p,sestavine,tip_prodaje,tipi)
    p.showPage()
    p.save()
    return response 

def pdf_baze(request,zaloga,tip_baze, pk):
    zaloga = Zaloga.objects.get(pk = zaloga)
    tip = request.GET.get('tip',"all")
    baza = zaloga.baza_set.all().get(pk=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="baza.pdf"'
    p = canvas.Canvas(response)
    p.translate(40,850)
    pdf.tabela_baze(p,baza,tip,800)
    p.showPage()
    p.save()
    return response 

def pdf_narocil(request,zaloga):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="baza.pdf"'
    p = canvas.Canvas(response)
    p.translate(40,850)
    vnosi, stranke = analiza_narocil(request,zaloga)
    headers = ["Naziv:", "Skupno število:"]
    keys = ["naziv", "skupno_stevilo"]
    top = pdf.tabela_vnosov(p, stranke,headers,keys,)
    headers = ["Dimenzija:", "Tip:", "Narocila:", "Zaloga:","Razlika:"]
    keys = ["dimenzija","tip","stevilo","zaloga","razlika"]
    top = pdf.tabela_vnosov(p,vnosi, headers, keys, top)
    p.showPage()
    p.save()
    return response

def pdf_razlike(request,zaloga,tip_baze,pk):
    zaloga = Zaloga.objects.get(pk = zaloga)
    baza = zaloga.baza_set.all().get(pk=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="razlike.pdf"'
    p = canvas.Canvas(response)
    p.translate(40,850)
    pdf.tabela_razlike_inventure(p,baza,800)
    p.showPage()
    p.save()
    return response 

def pdf_dnevne_prodaje(request,zaloga,pk_prodaje,tip):
    dnevna_prodaja = Dnevna_prodaja.objects.get(pk = pk_prodaje)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="dnevna_prodaja.pdf"'
    p = canvas.Canvas(response)
    p.translate(40,800) 
    p.drawString(180,0,'Pregled prodaje ' + dnevna_prodaja.title)
    pdf.tabela_dnevne_prodaje(p,dnevna_prodaja,tip)
    p.showPage()
    p.save()
    return response 

def pdf_skupnega_pregleda(request,zaloga):
    baze = Baza.objects.filter(zaloga = zaloga, status="aktivno", tip="vele_prodaja")
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="baza.pdf"'
    p = canvas.Canvas(response)
    p.translate(40,850)
    pdf.tabela_baz(p,baze)
    p.showPage()
    p.save()
    return response

def pdf_porocila_prometa(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="porocilo.pdf"'
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
    p = canvas.Canvas(response)
    p.translate(40,850)
    pdf.tabela_porocila(p,od,do,promet)
    p.showPage()
    p.save()
    return response