from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.pdfgen import canvas
import datetime
import json 
from zaloga.models import Zaloga

zaloga = Zaloga.objects.all().first()

with open('slovar.json') as dat:
        slovar = json.load(dat)

ZGORNJA_MEJA = 830
SPODANJA_MEJA = 30
LEVA_MEJA = 40
VISINA_VRSTICE = 20

def tabela(p, data, style, colWidths=None, rowHeights=VISINA_VRSTICE, jezik = "spa"):
    if colWidths == None:
        colWidths = 420 // len(data[0])
    t = Table(data,colWidths=colWidths,rowHeights=rowHeights)
    t.setStyle(style)
    t.wrapOn(p, aW=300, aH=50 )
    t.drawOn(p, x=50, y=-40)

def naslednja_vrstica(p,top,spodnja = SPODANJA_MEJA, zgornja = ZGORNJA_MEJA, leva = LEVA_MEJA, visina = VISINA_VRSTICE, jezik = "spa"):
    if top > spodnja:
        p.translate(0,-(visina))
        top -= visina
    else:
        p.showPage()
        p.translate(leva,zgornja)
        top = zgornja - visina
    return top

def tabela_zaloge(p, sestavine, tipi, top=800, jezik = "spa"):
    kratki_tipi = [tip[0] for tip in tipi]  
    dolgi_tipi = [tip[1] for tip in tipi]
    data=  [[slovar['Dimenzija'][jezik]] + dolgi_tipi] 
    style = TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),      
                        ])
    tabela(p,data,style)
    top -= 3*VISINA_VRSTICE
    top = naslednja_vrstica(p,top)
    for sestavina in sestavine:
        zaloga = []
        for tip in kratki_tipi:
            zaloga.append(sestavina[tip])
        data= [[sestavina['dimenzija__dimenzija']] + zaloga]
        style= TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                            ('BOX', (0,0), (-1,-1), 0.5, colors.black),      
                            ])
        tabela(p,data,style)
        top = naslednja_vrstica(p, top) 
    top = zaloga_skupno(p,sestavine,kratki_tipi,top)

def cenik(p,sestavine,tip_prodaje,tipi,top=800, jezik = "spa"):
    kratki_tipi = [tip[0] for tip in tipi]  
    dolgi_tipi = [tip[1] for tip in tipi]
    data=  [[slovar['Dimenzija'][jezik]] + dolgi_tipi] 
    style = TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),      
                        ])
    tabela(p,data,style)
    top -= 3*VISINA_VRSTICE
    top = naslednja_vrstica(p,top)
    for sestavina in sestavine:
        cene = []
        for cena in sestavina.cena_set.all().filter(prodaja = tip_prodaje, tip__in = kratki_tipi):
            cene.append(str(cena.cena) + "$")
        data= [[sestavina.dimenzija.dimenzija] + cene]
        style= TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                            ('BOX', (0,0), (-1,-1), 0.5, colors.black),      
                            ])
        tabela(p,data,style)
        top = naslednja_vrstica(p, top)


def tabela_baze(p, baza, top = 800, jezik = "spa"):
    if baza.tip == "prevzem":
        top = title_prevzema(p,baza)
    elif baza.tip == "vele_prodaja":
        top = title_vele_prodaje(p,baza)
    else:
        top = title_baze(p,baza)
    data=  [[slovar['Dimenzija'][jezik], slovar['Tip'][jezik], slovar['Stevilo'][jezik], slovar['Cena'][jezik], slovar['Skupna cena'][jezik]]] 
    style = TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),      
                        ])
    tabela(p,data,style)
    top = naslednja_vrstica(p,top)
    for vnos in baza.vnos_set.all().order_by("dimenzija"):
        data = [[
            vnos.dimenzija,
            vnos.tip, 
            vnos.stevilo, 
            str(vnos.cena) + "$" if baza.tip == "vele_prodaja" else "/", 
            str(vnos.skupna_cena) + "$" if baza.tip == "vele_prodaja" else "/"]] 
        style= TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),      
                        ])
        tabela(p,data,style)
        top = naslednja_vrstica(p,top)
    if baza.tip == "vele_prodaja":
        top = zadnja_vrstica_vele_prodaje(p,baza,top)
    else:
        top = zadnja_vrstica_baze(p,baza,top)
    podpis(p,top)

def tabela_dnevne_prodaje(p,prodaja, tip_tabele, top = 800, jezik = "spa"):
    if tip_tabele == "activity_log":
        data = [[slovar['Cas'][jezik], slovar['Dimenzija'][jezik], slovar['Tip'][jezik], slovar['Stevilo'][jezik], slovar['Cena'][jezik]]] 
    elif tip_tabele == "prodane":
        data = [[slovar['Dimenzija'][jezik], slovar['Tip'][jezik], slovar['Stevilo'][jezik], slovar['Cena'][jezik]]] 
    style = TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.5, colors.black),      
        ])
    tabela(p,data,style)
    top = naslednja_vrstica(p,top)
    if tip_tabele == "activity_log":
        for prodana in prodaja.activity_log:
            data = [[
                str(prodana['cas'])[:5],
                prodana['dimenzija'],
                prodana['tip'], 
                prodana['stevilo'], 
                str(prodana['cena']) + ' $' ]]
            style= TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                    ('BOX', (0,0), (-1,-1), 0.5, colors.black),      
                    ])
            tabela(p,data,style)
            top = naslednja_vrstica(p,top)    
    elif tip_tabele == "prodane":
        prodane = prodaja.prodane
        for prodana in prodane:
            data = [[
                prodane[prodana]['dimenzija'],
                prodane[prodana]['tip'],
                prodane[prodana]['stevilo'], 
                str(prodane[prodana]['cena']) + ' $']] 
            style = TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                    ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                    ('BOX', (0,0), (-1,-1), 0.5, colors.black),      
                    ])
            tabela(p,data,style)
            top = naslednja_vrstica(p,top)
    top = zadnja_vrstica_dnevne_prodaje(p,prodaja,top)

def zadnja_vrstica_dnevne_prodaje(p,prodaja,top, jezik = "spa"):
    skupno = prodaja.skupno_stevilo
    cena = str(prodaja.skupna_cena) + ' $'
    data=  [[slovar['Skupno stevilo'][jezik] + ':', skupno, slovar['Skupna cena'][jezik] + ':', cena]] 
    style= TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),      
                        ])
    tabela(p,data,style)
    return naslednja_vrstica(p,top)

def zadnja_vrstica_baze(p,baza,top, jezik = "spa"):
    skupno = baza.skupno_stevilo
    data=  [[slovar['Skupno stevilo'][jezik] + ':', baza.skupno_stevilo, '/']] 
    style= TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),      
                        ])
    tabela(p,data,style,colWidths=[168,84,168])
    return naslednja_vrstica(p,top)

def zadnja_vrstica_vele_prodaje(p,baza,top, jezik = "spa"):
    skupno = baza.skupno_stevilo
    data=  [[slovar['Skupno stevilo'][jezik] + ':', baza.skupno_stevilo, slovar['Cena'][jezik] + ':',str(baza.skupna_cena) + "$"]] 
    style= TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),      
                        ])
    tabela(p,data,style,colWidths=[168,84,84,84])
    top = naslednja_vrstica(p,top)
    data=  [[slovar['Popust'][jezik] + ':', str(baza.popust) + " %", slovar['Cena popusta'][jezik] + ':', str(baza.cena_popusta) + '$']] 
    style= TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),      
                        ])
    tabela(p,data,style,colWidths=[84,84,168,84])
    top = naslednja_vrstica(p,top)
    data=  [[slovar['Prevoz'][jezik] + ':', str(baza.prevoz) + " $", slovar['Cena prevoza'][jezik] + ':', str(baza.cena_prevoza) + '$']] 
    style= TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),      
                        ])
    tabela(p,data,style,colWidths=[84,84,168,84])
    top = naslednja_vrstica(p,top)
    data=  [[slovar['Koncna cena'][jezik] + ':', str(baza.koncna_cena) + "$"]] 
    style= TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),      
                        ])
    tabela(p,data,style,colWidths=[336,84])
    return naslednja_vrstica(p,top)

def zaloga_skupno(p,sestavine,tipi,top,jezik="spa"):
    stevilo = [0 for tip in tipi]
    cena = [0 for tip in tipi]
    cenik = zaloga.cenik()
    for sestavina in sestavine:
        n = 0
        for tip in tipi:
            stevilo[n] += sestavina[tip]
            cena[n] += cenik[sestavina['dimenzija__dimenzija']][tip] * sestavina[tip]
            n += 1
    for n in range(len(cena)):
        cena[n] = str(cena[n]) + '$'

    data=  [[slovar['Skupno stevilo'][jezik] + ':'] + stevilo] 
    style= TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),      
                        ])
    tabela(p,data,style)
    top = naslednja_vrstica(p,top)
    data=  [[slovar['Vrednost'][jezik] + ':'] + cena] 
    style= TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),      
                        ])
    tabela(p,data,style)
    return naslednja_vrstica(p,top)

##################################TITLI##################################################
def title_baze(p,baza,top = 800, jezik = "spa"):
    p.translate(10,0)
    data = [[slovar['Podatki baze'][jezik] + ':',slovar['Podatki uporabnika'][jezik] + ':']]
    style = TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER')])
    tabela(p,data,style,[200,200])
    top = naslednja_vrstica(p,top)
    top = naslednja_vrstica(p,top)
    top = naslednja_vrstica(p,top,visina=30)
    data = [
        [slovar['Tip'][jezik] + ':',baza.tip,slovar['Naziv'][jezik] + ':',baza.author.username],
        [slovar['Title'][jezik] + ':',baza.title, slovar['Telefon'][jezik] + ':',"/"],
        [slovar['Datum'][jezik] + ':',baza.datum,'E-mail', '/']
        ]
    style = TableStyle([('ALIGN',(0,0),(-1,-1),'LEFT')])
    tabela(p,data,style,[80,120,80,120])
    p.translate(-10,+10)
    top += 10
    for _ in range(3):
        top =  naslednja_vrstica(p,top)
    return top

def title_prevzema(p,baza,top = 800, jezik = "spa"):
    p.translate(-15,0)
    data = [[slovar['Podatki baze'][jezik] + ':',slovar['Podatki kontejnerja'][jezik] + ':', slovar['Podatki uporabnika'][jezik] + ':']]
    style = TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER')])
    tabela(p,data,style,[130,160,160])
    top = naslednja_vrstica(p,top)
    top = naslednja_vrstica(p,top)
    top = naslednja_vrstica(p,top,visina=30)
    data = [
        [slovar['Tip'][jezik] + ':',baza.tip,slovar['Stevilo'][jezik] + ':',baza.kontejner.stevilka,slovar['Ime'][jezik] + ':',baza.author.username],
        [slovar['Title'][jezik] + ':',baza.title,slovar['Posiljatelj'][jezik] + ':',baza.kontejner.get_posiljatelj_display(), slovar['Telefon'][jezik] + ':' ,"/"],
        [slovar['Datum'][jezik] + ':',baza.datum,slovar['Drzava'][jezik] + ':',baza.kontejner.get_drzava_display(),'E-mail','/']
        ]
    style = TableStyle([('ALIGN',(0,0),(-1,-1),'LEFT')])
    tabela(p,data,style,[55,85,65,95,65,95])
    p.translate(+15,+10)
    for _ in range(3):
        top =  naslednja_vrstica(p,top)
    return top

def title_vele_prodaje(p,baza,top = 800, jezik = "spa"):
    p.translate(-15,0)
    data = [[slovar['Podatki baze'][jezik] + ':',slovar['Podatki stranke'][jezik] + ':', slovar['Podatki prodajalca'][jezik] + ':']]
    style = TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER')])
    tabela(p,data,style,[130,160,160])
    top = naslednja_vrstica(p,top)
    top = naslednja_vrstica(p,top)
    top = naslednja_vrstica(p,top,visina=30)
    data = [
        [slovar['Tip'][jezik] + ':', slovar[baza.tip][jezik] , slovar['Naziv'][jezik] + ':', baza.stranka.ime, slovar['Naziv'][jezik] + ':', baza.author.username],
        [slovar['Title'][jezik] + ':', baza.title,slovar['Naslov'][jezik] + ':', baza.stranka.naslov.naslov, slovar['Telefon'][jezik] + ':',baza.stranka.telefon],
        [slovar['Datum'][jezik] + ':', baza.datum,slovar['Kontakt'][jezik] + ':', baza.stranka.telefon,'E-mail:',baza.stranka.mail]
        ]
    style = TableStyle([('ALIGN',(0,0),(-1,-1),'LEFT')])
    tabela(p,data,style,[55,85,65,95,65,95])
    p.translate(+15,+10)
    for _ in range(3):
        top =  naslednja_vrstica(p,top)
    return top

def podpis(p,top, jezik = "spa"):
    top = naslednja_vrstica(p,top,visina=60, spodnja = 40)
    p.drawString(300,0, slovar['Podpis'][jezik] + ':  ____________________')
    return top  