from django.shortcuts import render, redirect
from proizvodnja.serializers import BazaSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Baza, LastnostSestavine, PoslovnaEnota, VnosBaze, Zaloga
import datetime

# Create your views here.

# API VIEWS

@api_view(["POST"])
def uveljavi_inventuro(request):
    inventura = InventuraSerializer(request.data)
    inventura.create()
    return Response({"message": "true"})

class BazaView(APIView):

    def post(self, request):
        baza_json = request.data["baza"]
        baza = Baza.objects.create(
            zaloga_id = baza_json["zaloga"],
            naziv = baza_json["naziv"],
            tip = "inventura",
            status = "aktivno",
            datum = baza_json.get("datum",datetime.datetime.now())
        )
        vnosi_json = request.data["vnosi"]
        print(vnosi_json)
        vnosi = []
        for vnos in vnosi_json:
            vnosi.append(VnosBaze(
                baza = baza,
                sestavina_id = vnos["sestavina"],
                lastnostSestavine_id = vnos.get("lastnostSestavine",None),
                stevilo = vnos["stevilo"],
                cas = vnos.get("cas",datetime.datetime.now())

            ))
        VnosBaze.objects.bulk_create(vnosi)
        if baza_json["status"] == "veljavno":
            baza.uveljavi()
        return Response(BazaSerializer(baza).data)


def poslovne_enote(request):
    slovar = {
        "poslovne_enote": PoslovnaEnota.objects.all()
    }
    return render(request, "poslovne_enote.html", slovar)

def poslovna_enota(request, poslovna_enota_pk):
    poslovna_enota = PoslovnaEnota.objects.get(pk=poslovna_enota_pk)
    zaloge = Zaloga.objects.filter(poslovnaEnota = poslovna_enota)
    """ slovar = {
        "poslovna_enota": poslovna_enota,
        "zaloge": zaloge
    }
    return render(request, "poslovne_enote.html", slovar) """
    return redirect("zaloga", poslovna_enota_pk=poslovna_enota_pk, zaloga_pk = zaloge.first().pk)
    

def zaloga(request, poslovna_enota_pk, zaloga_pk):
    poslovna_enota = PoslovnaEnota.objects.get(pk=poslovna_enota_pk)
    zaloga = Zaloga.objects.get(pk = zaloga_pk, poslovnaEnota__pk = poslovna_enota_pk)
    slovar = {
        "poslovna_enota": poslovna_enota,
        "zaloga": zaloga
    }
    return render(request, "zaloga.html", slovar)

def nova_zaloga(request, poslovna_enota_pk):
    pass

