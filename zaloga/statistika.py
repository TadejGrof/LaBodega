from zaloga.models import *


zaporedni_prevzemi = [5,10,15,20]

zaloga = Zaloga.objects.first()
posiljatelj = "bozo"

prevzemi = Baza.objects.filter(kontejner__posiljtelj = posiljatelj, zaloga = zaloga, status = "veljavno", tip ="prevzem").order_by("-datum")

def statistika(zaporedni_prevzemi=zaporedni_prevzemi):
    pass

