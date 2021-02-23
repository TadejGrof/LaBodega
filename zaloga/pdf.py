from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.pdfgen import canvas
import datetime
import json
from zaloga.models import Zaloga,Vnos, Sestavina

centerStyle  = TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER')])

style = TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
                        ])

with open('slovar.json') as dat:
        slovar = json.load(dat)

ZGORNJA_MEJA = 830
SPODANJA_MEJA = 100
LEVA_MEJA = 40
VISINA_VRSTICE = 20

def tabela(p, data, style, colWidths=None, rowHeights=VISINA_VRSTICE, jezik = "spa"):
    if colWidths == None:
        colWidths = 420 // len(data[0])
    t = Table(data,colWidths=colWidths,rowHeights=rowHeights)
    t.setStyle(style)
    t.wrapOn(p, aW=300, aH=50 )
    t.drawOn(p, x=50, y=-40)

def naslednja_vrstica(p,top,spodnja = SPODANJA_MEJA, zgornja = ZGORNJA_MEJA, leva = LEVA_MEJA, visina = VISINA_VRSTICE, jezik = "spa",header = None):
    if top > spodnja:
        p.translate(0,-(visina))
        top -= visina
    else:
        p.showPage()
        p.translate(leva,zgornja)
        top = zgornja - visina
        if header != None:
            tabela(p,header[0],header[1])
            top = naslednja_vrstica(p,top)
    return top

def tabela_zaloge(p, zaloga, sestavine, tipi, top=800, jezik = "spa"):
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
        stanje = []
        for tip in kratki_tipi:
            stanje.append(sestavina[tip])
        data= [[sestavina['dimenzija__dimenzija']] + stanje]
        style= TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                            ('BOX', (0,0), (-1,-1), 0.5, colors.black),
                            ])
        tabela(p,data,style)
        top = naslednja_vrstica(p, top)
    top = zaloga_skupno(p,zaloga,sestavine,kratki_tipi,top)

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
        nicelne = True
        for cena in sestavina.cena_set.all().filter(prodaja = tip_prodaje, tip__in = kratki_tipi):
            if cena.cena > 0:
                cene.append(str(cena.cena) + "$")
                nicelne = False
            else:
                cene.append('/')
        if not nicelne:
            data= [[sestavina.dimenzija.dimenzija] + cene]
            style= TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                                ('BOX', (0,0), (-1,-1), 0.5, colors.black),
                                ])
            tabela(p,data,style)
            top = naslednja_vrstica(p, top)

def tabela_porocila(p,od,do,promet, top = 800, jezik = "spa"):
    header = [["Report"]]
    tabela(p,header,style)
    top = naslednja_vrstica(p,top)
    podatki = [["From:",od,"To:",do]]
    tabela(p,podatki,style)
    top = naslednja_vrstica(p,top)
    top = naslednja_vrstica(p,top)
    skupno = 0
    header = [["Date:","Type:","Title:","Amount:","All:"]]
    tabela(p,header,style)
    top = naslednja_vrstica(p,top)
    for podatek in promet[::-1]:
        znesek = podatek["znesek"]
        skupno += znesek
        if znesek > 0:
            znesek = "+" + str(znesek) + "$"
        else:
            znesek = str(znesek) + "$"
        
        if skupno > 0:
            skupno_str = "+" + str(skupno) + "$"
        else:
            skupno_str = str(skupno) + "$"
        data = [[podatek["datum"],podatek["tip"],podatek["title"],znesek,skupno_str]]
        tabela(p,data,style)
        top = naslednja_vrstica(p,top)

def tabela_baze(p, baza, tip, top = 800, jezik = "spa"):
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
    vnosi = baza.vnos_set.all().order_by("dimenzija")
    if tip != "all":
        vnosi = vnosi.filter(tip=tip)
    brezplacne = []
    for vnos in vnosi:
        if vnos.cena == 0:
            brezplacne.append(vnos)
        else:
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
        top = zadnja_vrstica_vele_prodaje(p,baza,tip,top,brezplacne)
    else:
        top = zadnja_vrstica_baze(p,baza,tip,top)
    podpis(p,top)

def tabela_razlike_inventure(p,baza,top=800,jezik = "spa"):
    header = [slovar['Dimenzija'][jezik],
            slovar['Tip'][jezik], 
            slovar['Vnos'][jezik], 
            slovar['Zaloga'][jezik], 
            slovar['Razlika'][jezik]
        ]
    style = TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
                        ])
    header = [[header],style]
    tabela(p,header[0],header[1])
    top = naslednja_vrstica(p,top)

    sestavine = Sestavina.objects.all().filter(zaloga = baza.zaloga)
    
    skupna_razlika = 0
    for vnos in baza.vnos_set.all().order_by("dimenzija"):
        stevilo = vnos.stevilo
        sestavina = sestavine.get(dimenzija = vnos.dimenzija)
        zaloga = getattr(sestavina, vnos.tip)
        razlika = stevilo - zaloga
        skupna_razlika += razlika
        if razlika != 0:
            vrstica = [vnos.dimenzija.dimenzija,vnos.tip,stevilo, zaloga, razlika]
            style = TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                            ('BOX', (0,0), (-1,-1), 0.5, colors.black),
                            ])
            tabela(p,[vrstica],style)
            top = naslednja_vrstica(p,top,header = header)    
    # zadnja vrstica
    vrstica = ["Skupna razlika:", skupna_razlika]
    style = TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
                        ])
    tabela(p,[vrstica],style)
    top = naslednja_vrstica(p,top)   

def tabela_baz(p,baze,top = 800, jezik = "spa"):
    vnosi = Vnos.objects.filter(baza__in = baze).order_by('dimenzija').values('baza__pk','dimenzija__dimenzija','dimenzija__radius','tip','stevilo','pk','baza__stranka__pk')
    razlicne_dimenzije = {}
    for vnos in vnosi:
        dimenzija = vnos['dimenzija__dimenzija']
        tip = vnos['tip']
        dimenzija_tip = dimenzija + '_' + tip
        radius = vnos['dimenzija__radius']
        stevilo = vnos['stevilo']
        baza = vnos['baza__pk']
        vnos = vnos['pk']
        if not dimenzija_tip in razlicne_dimenzije:
            razlicne_dimenzije[dimenzija_tip] = {'dimenzija':dimenzija,'radius':radius,'tip':tip,'baze':{baza:{vnos:stevilo}}}
        elif not baza in razlicne_dimenzije[dimenzija_tip]['baze']:
            razlicne_dimenzije[dimenzija_tip]['baze'][baza] = {vnos:stevilo}
        else:
            razlicne_dimenzije[dimenzija_tip]['baze'][baza][vnos] = stevilo

    header = [slovar['Dimenzija'][jezik],""," " + slovar['Tip'][jezik]] + [baza.stranka.ime[:3] for baza in baze] + [""]
    style = TableStyle([('ALIGN',(2,0),(-1,-1),'CENTER'),
                        ('ALIGN',(0,0),(1,0),'LEFT'),
                        ('INNERGRID', (2,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
                        ])
    header = [[header],style]
    tabela(p,header[0],header[1])
    top = naslednja_vrstica(p,top)
    def stevilo_baze(podatki,baza):
        try:
            vnosi = podatki[baza]
        except:
            try:
                vnosi = podatki[baza.pk]
            except:
                return 0
        stevilo = 0
        for vnos in vnosi:
            stevilo += vnosi[vnos]
        return stevilo

    for dimenzija in razlicne_dimenzije:
        podatki = razlicne_dimenzije[dimenzija]["baze"]
        skupno = 0
        for baza in podatki:
            skupno += stevilo_baze(podatki,baza)
        
        vrstica = [dimenzija.split('_')[0],"",dimenzija.split('_')[1]] + [stevilo_baze(podatki,baza) if baza.pk in podatki else 0 for baza in baze] + [skupno]
        style = TableStyle([('ALIGN',(2,0),(-1,-1),'CENTER'),
                            ('ALIGN',(0,0),(1,0),'LEFT'),
                            ('INNERGRID', (2,0), (-1,-1), 0.25, colors.black),
                            ('BOX', (0,0), (-1,-1), 0.5, colors.black),
                            ])
        tabela(p,[vrstica],style)
        top = naslednja_vrstica(p,top,header = header)

    skupno = ["Total:","",""]
    skupno_stevilo = 0
    for baza in baze:
        stevilo = baza.skupno_stevilo
        skupno_stevilo += stevilo
        skupno.append(stevilo)
    skupno.append(skupno_stevilo)
    skupno = [skupno]
    tabela(p,skupno,style)
    top = naslednja_vrstica(p,top)

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

def zadnja_vrstica_baze(p,baza,tip,top, jezik = "spa"):
    if tip == "all":
        skupno = baza.skupno_stevilo
    else:
        skupno = baza.skupnoStevilo(tip)
    data=  [[slovar['Skupno stevilo'][jezik] + ':', skupno, '/']]
    style= TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
                        ])
    tabela(p,data,style,colWidths=[168,84,168])
    return naslednja_vrstica(p,top)

def zadnja_vrstica_vele_prodaje(p,baza,tip,top,brezplacne, jezik = "spa"):
    if tip == "all":
        skupno = baza.skupno_stevilo
    else:
        skupno = baza.skupnoStevilo(tip)
    data=  [[slovar['Skupno stevilo'][jezik] + ':', skupno , slovar['Cena'][jezik] + ':',str(baza.skupna_cena) + "$"]]
    style= TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
                        ])
    tabela(p,data,style,colWidths=[84,84,168,84])
    top = naslednja_vrstica(p,top)
    data=  [[slovar['Popust'][jezik] + ':', str(baza.popust) + " %", slovar['Cena popusta'][jezik] + ':', str(baza.cena_popusta) + '$']]
    style= TableStyle([('ALIGN',(0,0),(-1,-1),'CENTER'),
                        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                        ('BOX', (0,0), (-1,-1), 0.5, colors.black),
                        ])
    tabela(p,data,style,colWidths=[84,84,168,84])
    top = naslednja_vrstica(p,top)
    for vnos in brezplacne:
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

def zaloga_skupno(p,zaloga,sestavine,tipi,top,jezik="spa"):
    stevilo = [0 for tip in tipi]
    cena = [0 for tip in tipi]
    cenik = zaloga.cenik()
    for sestavina in sestavine:
        n = 0
        for tip in tipi:
            try:
                stevilo[n] += sestavina[tip]
                cena[n] += cenik[sestavina['dimenzija__dimenzija']][tip] * sestavina[tip]
            except:
                stevilo[n] = 0
                cena[n] = 0
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
    data = [[slovar['Tip'][jezik] + ':', slovar[baza.tip][jezik],
            slovar['Title'][jezik] + ':', baza.title,
            slovar['Datum'][jezik] + ':', baza.datum]]
    tabela(p,data,centerStyle,[40,140,50,80,50,80])
    top = naslednja_vrstica(p,top,visina=30)
    data = [[slovar['Podatki stranke'][jezik] + ':', slovar['Podatki prodajalca'][jezik] + ':']]
    tabela(p,data,centerStyle,[250,250])
    top = naslednja_vrstica(p,top)
    top = naslednja_vrstica(p,top)
    top = naslednja_vrstica(p,top)
    top = naslednja_vrstica(p,top)
    top = naslednja_vrstica(p,top,visina=30)
    data = [
        [slovar['Naziv'][jezik] + ':', baza.stranka.ime, slovar['Naziv'][jezik] + ':', baza.author.profil.celo_ime],
        [slovar['Davcna'][jezik] + ': ' , baza.stranka.davcna, slovar['Telefon'][jezik] + ':',baza.author.profil.telefon],
        [slovar['Kontakt'][jezik] + ':', baza.stranka.telefon,'E-mail:', baza.author.email],
        [slovar['Naslov'][jezik] + ':', baza.stranka.naslov.mesto, slovar['Banka'][jezik] + ':', baza.author.profil.tip_banke],
        [slovar['Ulica'][jezik] + ':', baza.stranka.naslov.naslov, slovar['Stevilka racuna'][jezik] + ':', baza.author.profil.stevilka_racuna]
        ]
    style = TableStyle([('ALIGN',(0,0),(-1,-1),'LEFT')])
    tabela(p,data,style,[55,220,65,150])
    p.translate(+15,+10)
    for _ in range(3):
        top =  naslednja_vrstica(p,top)
    return top

def podpis(p,top, jezik = "spa"):
    top = naslednja_vrstica(p,top,visina=60, spodnja = 40)
    p.drawString(300,0, slovar['Podpis'][jezik] + ':  ____________________')
    return top

