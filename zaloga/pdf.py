from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.pdfgen import canvas
import datetime

ZGORNJA_MEJA = 830
SPODANJA_MEJA = 30
LEVA_MEJA = 40
VISINA_VRSTICE = 20

def tabela(p, data, style, colWidths=None, rowHeights=VISINA_VRSTICE):
    if colWidths == None:
        colWidths = 420 // len(data[0])
    t = Table(data,colWidths=colWidths,rowHeights=rowHeights)
    t.setStyle(style)
    t.wrapOn(p, aW=300, aH=50 )
    t.drawOn(p, x=50, y=-40)

def naslednja_vrstica(p,top,spodnja = SPODANJA_MEJA, zgornja = ZGORNJA_MEJA, leva = LEVA_MEJA, visina = VISINA_VRSTICE):
    if top > spodnja:
        p.translate(0,-(visina))
        top -= visina
    else:
        p.showPage()
        p.translate(leva,zgornja)
        top = zgornja - visina
    return top

def tabela_zaloge(p, sestavine, tipi, top=800):
    kratki_tipi = [tip[0] for tip in tipi]  
    dolgi_tipi = [tip[1] for tip in tipi]
    data=  [['Dimenzija'] + dolgi_tipi] 
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
            zaloga.append(getattr(sestavina,tip))
        data= [[sestavina.dimenzija.dimenzija] + zaloga]
        style= TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                            ('BOX', (0,0), (-1,-1), 0.5, colors.black),      
                            ])
        tabela(p,data,style)
        top = naslednja_vrstica(p, top)

def cenik(p,sestavine,tip_prodaje,tipi,top=800):
    kratki_tipi = [tip[0] for tip in tipi]  
    dolgi_tipi = [tip[1] for tip in tipi]
    data=  [['Dimenzija'] + dolgi_tipi] 
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


def tabela_baze(p, baza, top = 800):
    if baza.tip == "prevzem":
        top = title_prevzema(p,baza)
    elif baza.tip == "vele_prodaja":
        top = title_vele_prodaje(p,baza)
    else:
        top = title_baze(p,baza)
    data=  [['Dimenzija', 'Tip', 'Stevilo', 'Cena', 'Skupna cena']] 
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
            vnos.cena if baza.tip == "vele_prodaja" else "/", 
            vnos.skupna_cena if baza.tip == "vele_prodaja" else "/"]] 
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

def tabela_dnevne_prodaje(p,prodaja, tip_tabele, top = 800):
    if tip_tabele == "activity_log":
        data = [['Cas', 'Dimenzija', 'Tip', 'Stevilo', 'Cena']] 
    elif tip_tabele == "prodane":
        data = [['Dimenzija', 'Tip', 'Stevilo', 'Cena']] 
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

def zadnja_vrstica_baze(p,baza,top):
    skupno = baza.skupno_stevilo
    data=  [['Skupno stevilo:', baza.skupno_stevilo, '/']] 
    style= TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),      
                        ])
    tabela(p,data,style,colWidths=[168,84,168])
    return naslednja_vrstica(p,top)

def zadnja_vrstica_vele_prodaje(p,baza,top):
    skupno = baza.skupno_stevilo
    data=  [['Skupno stevilo:', baza.skupno_stevilo, 'Cena',str(baza.skupna_cena) + "$"]] 
    style= TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),      
                        ])
    tabela(p,data,style,colWidths=[168,84,84,84])
    top = naslednja_vrstica(p,top)
    data=  [['Popust:', str(baza.popust) + " %", 'Cena popusta:', str(baza.cena_popusta) + '$']] 
    style= TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),      
                        ])
    tabela(p,data,style,colWidths=[84,84,168,84])
    top = naslednja_vrstica(p,top)
    data=  [['Koncna cena:', str(baza.koncna_cena) + "$"]] 
    style= TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),      
                        ])
    tabela(p,data,style,colWidths=[336,84])
    return naslednja_vrstica(p,top)

def zadnja_vrstica_tabele_zaloge(p):
    p.translate(0,-20)
    skupno = zaloga.skupno_stevilo
    data=  [['skupno', 'stevilo:', skupno[1], 'stevilo:', skupno[2]]
            ] 
    t = Table(data, colWidths=75, rowHeights=20)
    t.setStyle(TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),      
                        ]))
    t.wrapOn(p, aW=300, aH=50 )
    t.drawOn(p, x=50, y=-0)


##################################TITLI##################################################
def title_baze(p,baza,top = 800):
    p.translate(10,0)
    data = [['Podatki baze:','Podatki uporabnika:']]
    style = TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER')])
    tabela(p,data,style,[200,200])
    top = naslednja_vrstica(p,top)
    top = naslednja_vrstica(p,top)
    top = naslednja_vrstica(p,top,visina=30)
    data = [
        ['Tip:',baza.tip,'Ime:',baza.author.username],
        ['Title:',baza.title, 'Telefon:',"031"],
        ['Datum',baza.datum,'E-mail', 'dsdsdsdsadsa']
        ]
    style = TableStyle([('ALIGN',(0,0),(-1,-1),'LEFT')])
    tabela(p,data,style,[80,120,80,120])
    p.translate(-10,+10)
    top += 10
    for _ in range(3):
        top =  naslednja_vrstica(p,top)
    return top

def title_prevzema(p,baza,top = 800):
    p.translate(-15,0)
    data = [['Podatki baze:','Podatki kontejnerja:','Podatki uporabnika:']]
    style = TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER')])
    tabela(p,data,style,[130,160,160])
    top = naslednja_vrstica(p,top)
    top = naslednja_vrstica(p,top)
    top = naslednja_vrstica(p,top,visina=30)
    data = [
        ['Tip:',baza.tip,'Stevilka:',baza.kontejner.stevilka,'Ime:',baza.author.username],
        ['Title:',baza.title,'Posiljatelj:',baza.kontejner.posiljatelj, 'Telefon:',"031"],
        ['Datum',baza.datum,'Drzava:',baza.kontejner.drzava,'E-mail','dsdsdsdsadsa']
        ]
    style = TableStyle([('ALIGN',(0,0),(-1,-1),'LEFT')])
    tabela(p,data,style,[55,85,65,95,65,95])
    p.translate(+15,+10)
    for _ in range(3):
        top =  naslednja_vrstica(p,top)
    return top

def title_vele_prodaje(p,baza,top = 800):
    p.translate(-15,0)
    data = [['Podatki baze:','Podatki kontejnerja:','Podatki prodajalca:']]
    style = TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER')])
    tabela(p,data,style,[130,160,160])
    top = naslednja_vrstica(p,top)
    top = naslednja_vrstica(p,top)
    top = naslednja_vrstica(p,top,visina=30)
    data = [
        ['Tip:',baza.tip,'Ime:', baza.stranka.ime,'Ime:',baza.author.username],
        ['Title:',baza.title,'Naslov:', baza.stranka.naslov.naslov, 'Telefon:',"031"],
        ['Datum',baza.datum,'Kontakt:', baza.stranka.telefon,'E-mail','dsdsdsdsadsa']
        ]
    style = TableStyle([('ALIGN',(0,0),(-1,-1),'LEFT')])
    tabela(p,data,style,[55,85,65,95,65,95])
    p.translate(+15,+10)
    for _ in range(3):
        top =  naslednja_vrstica(p,top)
    return top

def podpis(p,top):
    top = naslednja_vrstica(p,top,visina=60, spodnja = 40)
    p.drawString(300,0,'Firma:  ____________________')
    return top  