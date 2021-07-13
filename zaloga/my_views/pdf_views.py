from django.shortcuts import render
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
 
#zaloga = Zaloga.objects.first()

def pdf_zaloge(request,zaloga):
    zaloga = Zaloga.objects.get(pk = zaloga)
    radij = request.GET.get('radius')
    sestavine = zaloga.sestavine.all()
    nicelne = request.GET.get('nicelne','true')
    rezervirane = request.GET.get('rezervirane','false')
    if radij != 'all':
        sestavine = zaloga.sestavine.all().filter(dimenzija__radius = radij)
    tipi = []
    for tip in zaloga.tipi_sestavin.all():
        if request.GET.get(tip.kratko):
            tipi.append(tip)
    sestavine = sestavine.filter(tip__in=tipi).all_values().zaloga_values(zaloga)
    if nicelne == "false":
        sestavine = sestavine.exclude(stanje=0)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="zaloga.pdf"'
    
    p = canvas.Canvas(response)
    p.translate(40,800)
    p.drawString(200,0,'Pregled zaloge')
    pdf.tabela_zaloge(p,zaloga,sestavine,tipi)
    p.showPage()
    p.save()
    return response 
    
def pdf_cenika(request,zaloga):
    radius = request.GET.get('radius',"all")
    zaloga = Zaloga.objects.get(pk=zaloga)
    sestavine = zaloga.sestavine.all()
    if radius != 'all' and radius != "":
        sestavine = sestavine.filter(dimenzija__radius = radius)
    tipi = []
    for tip in zaloga.tipi_sestavin.all():
        if request.GET.get(tip.kratko):
            tipi.append(tip)
    sestavine = sestavine.filter(tip__in=tipi).cenik_values(zaloga)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="cenik.pdf"'
    p = canvas.Canvas(response)
    p.translate(40,800)
    p.drawString(200,0,'Cenik prodaje')
    pdf.cenik(p,sestavine,tipi)
    p.showPage()
    p.save()
    return response 

def pdf_baze(request,zaloga,tip_baze, pk):
    zaloga = Zaloga.objects.get(pk = zaloga)
    tip = request.GET.get('tip',"all")
    try:
        tip = Tip.objects.get(kratko=tip)
    except:
        tip = None
    baza = zaloga.baza_set.all().get(pk=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="baza.pdf"'
    p = canvas.Canvas(response)
    p.translate(40,850)
    pdf.tabela_baze(p,baza,tip,800)
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
