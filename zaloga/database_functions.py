from django.db.models import IntegerField,FloatField,CharField
from django.db.models import F,Value,Subquery, Count, OuterRef, Sum, When, Case, Q
from django.db.models.functions import Concat,Cast, Coalesce, Round

def vnosi_values(vnosi):
    return vnosi.order_by("dimenzija").values(
            'dimenzija__dimenzija',
            'dimenzija__radius',
            'pk',
            'stevilo',
            'tip',
            'cena',
            'cena_nakupa') \
        .annotate(dim = F("dimenzija__dimenzija")) \
        .annotate(dimenzija_tip = Concat(F("dim"),Value("_"),F("tip"))) \
        .annotate(cena_nakupa_value = Cast(Coalesce(F("cena_nakupa"),0), output_field=FloatField())) \
        .annotate(cena_value = Cast(Coalesce(F("cena"),0), output_field=FloatField())) \
        .annotate(skupna_cena = Cast(F("cena_value") * F("stevilo"), output_field=FloatField())) \
        .annotate(skupna_cena_nakupa = Cast(F("cena_nakupa_value") * F("stevilo"), output_field=FloatField()))

def dnevne_prodaje_values(prodaje):
    return prodaje \
        .annotate(stevilo_racunov = Count("baza",filter=Q(baza__status__in=["veljavno","zaklenjeno"]))) \
        .annotate(skupno_stevilo = Coalesce(Sum("baza__vnos__stevilo", filter=Q(baza__status__in=["veljavno","zaklenjeno"])),0)) \
        .annotate(skupna_cena = Coalesce(Sum(Cast(F("baza__vnos__cena") * F("baza__vnos__stevilo"),output_field=FloatField()), filter=Q(baza__status__in=["veljavno","zaklenjeno"])),0)) \
        .annotate(koncna_cena = F("skupna_cena")) \
        .values()

def baze_values(baze):
    return baze.select_related("vnos") \
        .annotate(stevilka_kontejnerja = F("kontejner__stevilka")) \
        .annotate(tip_prevzema = Case(
            When(kontejner__isnull=False,then=Value("Kontejner")),
            When(zalogaPrenosa__isnull=False,then=Value("Prenos")),
            default=Value("Drugo"),
            output_field=CharField())) \
        .annotate(zaloga_prenosa = F("zalogaPrenosa")) \
        .annotate(posiljatelj = Case(
            When(tip_prevzema="Kontejner",then=F("kontejner__posiljatelj")),
            When(tip_prevzema="Prenos",then=Value("Skladisce")),
            default=Value("Drugo"),
            output_field=CharField())) \
        .annotate(drzava = F("kontejner__drzava")) \
        .annotate(naziv_stranke = F("stranka__naziv")) \
        .annotate(skupno_stevilo = Coalesce(Sum("vnos__stevilo"),0)) \
        .annotate(skupna_cena = Coalesce(Sum(F("vnos__stevilo") * Coalesce(F("vnos__cena"),0), output_field=FloatField()),0)) \
        .annotate(skupna_cena_nakupa = Sum(F("vnos__stevilo") * Coalesce(F("vnos__cena_nakupa"),0), output_field=FloatField())) \
        .annotate(cena_popusta = Round(F("skupna_cena") * Coalesce(F("popust"),0) / Value(100), output_field=FloatField())) \
        .annotate(cena_prevoza = Round(F("skupno_stevilo") * Coalesce(F("prevoz"),0), output_field=FloatField())) \
        .annotate(koncna_cena = F("skupna_cena") - F("cena_popusta") + F("cena_prevoza")) \
        .annotate(ladijski_prevoz_value = Coalesce(F("ladijski_prevoz"),0)) \
        .annotate(razlika = Coalesce(Round(F("skupna_cena") - F("skupna_cena_nakupa") - F("cena_popusta") + F("cena_prevoza") - F("ladijski_prevoz_value"), output_field=FloatField()),0)) \
        .values()

