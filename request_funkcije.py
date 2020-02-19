from zaloga.models import Zaloga, Dimenzija, Sestavina, Vnos
from program.models import Program
import json
from django.shortcuts import render

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
    je_stranka = False
    program = Program.objects.first()
    zaloga = Zaloga.objects.first()
    if request.user.profil.stranka != None:
        je_stranka = True
    slovar = {'je_stranka':je_stranka,'program':program,'slovar':vrni_slovar(request),'jezik':request.user.profil.jezik}
    slovar.update(baze)
    if not 'zaloga' in baze:
        slovar.update({'zaloga':zaloga})
    slovar.update({'zaloga_pk':slovar['zaloga'].pk})
    return render(request, html, slovar)