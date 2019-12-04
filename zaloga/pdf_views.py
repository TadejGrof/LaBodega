from django.shortcuts import render
from .models import Dimenzija, Sestavina, Vnos
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

def some_view(request):
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="somefilename.pdf"'

    # Create the PDF object, using the response object as its "file."
    p = canvas.Canvas(response)

    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.
    p.drawString(100, 100, "Hello world.")

    # Close the PDF object cleanly, and we're done.
    p.showPage()
    p.save()
    return response

def pdf_zaloge(request):
    radius = request.POST.get('radius')
    sestavine = zaloga.sestavina_set.all()
    tipi = zaloga.vrni_tipe
    if radius != 'all':
        sestavine = zaloga.sestavina_set.all().filter(radius = radius)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.translate(40,800)
    p.drawString(200,0,'Pregled zaloge')
    pdf.tabela_zaloge(p,sestavine,tipi)
    p.showPage()
    p.save()
    buffer.seek(0) 
    return FileResponse(buffer, as_attachment=True, filename='zaloga.pdf')    
    
def pdf_cenika(request,tip_prodaje):
    sestavine = zaloga.sestavina_set.all()
    tipi = zaloga.vrni_tipe
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.translate(40,800)
    if tip_prodaje == "vele_prodaja":
        p.drawString(200,0,'Cenik vele prodaje')
    elif tip_prodaje == "dnevna_prodaja":
        p.drawString(200,0,'Cenik dnevne prodaje')
    pdf.cenik(p,sestavine,tip_prodaje,tipi)
    p.showPage()
    p.save()
    buffer.seek(0) 
    return FileResponse(buffer, as_attachment=True, filename='cenik.pdf')  

def pdf_baze(request,tip_baze, pk):
    baza = zaloga.baza_set.all().get(pk=pk)
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.translate(40,850)
    pdf.tabela_baze(p,baza,800)
    p.showPage()
    p.save()
    buffer.seek(0) 
    return FileResponse(buffer, as_attachment=True, filename='prodaja.pdf')    

