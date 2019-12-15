from django.shortcuts import render
from .models import Kontejner, Stroski_Group, Strosek
from .models import Baza, Zaloga
from django.shortcuts import redirect
import datetime
from django.contrib.auth.decorators import login_required
import json 

zaloga = Zaloga.objects.all().first()

@login_required
def pregled(request):
    od = request.GET.get('od',datetime.date(2019,12,1))
    do = request.GET.get('do', datetime.date.today())
    stroski = stroski.filter(datum__gte = od, datum__lte = do)
    return pokazi_stran(request,'stroski/pregled_stroskov.html',{'stroski':stroski})

@login_required
def strosek(request):
    strosek = Stroski_Group.objects.all().filter(status = 'aktivno').first()
    kontejnerji = Kontejner.objects.all().order_by('-baza__datum')[:10].values('stevilka','pk')
    return pokazi_stran(request,'stroski/nov_strosek.html',{'strosek':strosek,'kontejnerji':kontejnerji})

@login_required
def nov_strosek(request):
    if request.method == "POST":
        title = request.POST.get('title')
        tip = request.POST.get('tip')
        datum = request.POST.get('datum')
        kontejner = None
        if tip == "kontejner":
            kontejner = Kontejner.objects.get(pk = int(request.POST.get('kontejner')))
        Stroski_Group.objects.create(
            title = title,
            tip = tip,
            datum = datum,
            kontejner = kontejner
        )
    return redirect('strosek')

@login_required
def uveljavi(requestl,pk):
    if request.method == "POST":
        strosek = Stroski_Group.objects.get(pk = pk)
        strosek.status = "veljavno"
        strosek.save()
    return redirect('pregled_stroskov')


###################################################################################
###################################################################################
###################################################################################

def vrni_slovar(request):
    with open('slovar.json') as dat:
        slovar = json.load(dat)
    return slovar

def pokazi_stran(request, html, baze={}):
    slovar = {'zaloga':zaloga,'slovar':vrni_slovar(request),'jezik':request.user.profil.jezik}
    slovar.update(baze)
    return render(request, html, slovar)
