from django.shortcuts import render
from .models import Dimenzija, Sestavina, Vnos, Dnevna_prodaja
from .models import Baza, Zaloga
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
 
zaloga = Zaloga.objects.first()

def pdf_zaloge(request):
    radius = request.GET.get('radius')
    sestavine = zaloga.sestavina_set.all()
    nicelne = request.GET.get('nicelne','true')
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

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="zaloga.pdf"'
    
    p = canvas.Canvas(response)
    p.translate(40,800)
    p.drawString(200,0,'Pregled zaloge')
    pdf.tabela_zaloge(p,sestavine,tipi)
    p.showPage()
    p.save()
    return response 
    
def pdf_cenika(request,tip_prodaje):
    radius = request.GET.get('radius')
    sestavine = zaloga.sestavina_set.all()
    if radius != 'all':
        sestavine = zaloga.sestavina_set.all().filter(dimenzija__radius = radius)
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

def pdf_baze(request,tip_baze, pk):
    baza = zaloga.baza_set.all().get(pk=pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="baza.pdf"'
    p = canvas.Canvas(response)
    p.translate(40,850)
    pdf.tabela_baze(p,baza,800)
    p.showPage()
    p.save()
    return response 

def pdf_dnevne_prodaje(request,pk,tip):
    dnevna_prodaja = Dnevna_prodaja.objects.get(pk = pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="dnevna_prodaja.pdf"'
    p = canvas.Canvas(response)
    p.translate(40,800)
    p.drawString(180,0,'Pregled prodaje ' + dnevna_prodaja.title)
    pdf.tabela_dnevne_prodaje(p,dnevna_prodaja,tip)
    p.showPage()
    p.save()
    return response 