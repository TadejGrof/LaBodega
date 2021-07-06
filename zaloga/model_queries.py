from django.db import models
from django.db.models import IntegerField,FloatField,CharField
from django.db.models import F,Value,Subquery, Count, OuterRef, Sum, When, Case, Q, Exists
from django.db.models.functions import Concat,Cast, Coalesce, Round

class BazaQuerySet(models.QuerySet):
    def aktivne_baze(self, zaloga):
        return self.filter(zaloga=zaloga, status="aktivno")

    def cakajoce_baze(self, zaloga):
        return self.filter(zaloga=zaloga, status="cakajoce")

    def author_values(self):
        return self \
        .annotate(username_creatorja = F("author__username")) \
        .annotate(username_uveljavitelja = F("author__username"))

    def dobavitelj_values(self):
        return self \
        .annotate(naziv_dobavitelja = Coalesce(F("dobavitelj__naziv"),Value(""))) \
        .annotate(telefon_dobavitelja = Coalesce(F("dobavitelj__telefon"),Value(""))) \
        .annotate(email_dobavitelja = Coalesce(F("dobavitelj__mail"),Value(""))) \
        .annotate(ulica_dobavitelja = Coalesce(F("dobavitelj__ulica"),Value(""))) \
        .annotate(status_dobavitelja = Coalesce(F("dobavitelj__status"),Value(""))) \
        .annotate(davcna_dobavitelja = Coalesce(F("dobavitelj__davcna"),Value(""))) 

    def stranka_values(self):
        return self \
        .annotate(naziv_stranke = Coalesce(F("stranka__naziv"),Value(""))) \
        .annotate(telefon_stranke = Coalesce(F("stranka__telefon"),Value(""))) \
        .annotate(email_stranke = Coalesce(F("stranka__mail"),Value(""))) \
        .annotate(ime_stranke = Coalesce(F("stranka__ime"),Value(""))) \
        .annotate(ulica_stranke = Coalesce(F("stranka__ulica"),Value(""))) \
        .annotate(status_stranke = Coalesce(F("stranka__status"),Value(""))) \
        .annotate(davcna_stranke = Coalesce(F("stranka__davcna"),Value(""))) 

    def skupno_values(self):
        return self \
        .annotate(skupno_stevilo = Coalesce(Sum("vnos__stevilo"),0)) \
        .annotate(skupna_cena = Coalesce(Sum(F("vnos__stevilo") * Coalesce(F("vnos__cena_prodaje"),0), output_field=FloatField()),0)) \
        .annotate(skupna_cena_nakupa = Sum(F("vnos__stevilo") * Coalesce(F("vnos__cena_nakupa"),0), output_field=FloatField())) \
        .annotate(razlika = F("skupna_cena") - F("skupna_cena_nakupa")) \
        .annotate(cena_popusta = Round(F("skupna_cena") * Coalesce(F("popust"),0) / Value(100), output_field=FloatField())) \
        .annotate(cena_prevoza = Round(F("skupno_stevilo") * Coalesce(F("prevoz"),0), output_field=FloatField())) \
        .annotate(koncna_cena = F("skupna_cena") - F("cena_popusta") + F("cena_prevoza"))

    def all_values(self):
        return self \
            .annotate(tip = F("proxy_name")) \
            .dobavitelj_values() \
            .stranka_values() \
            .author_values() \
            .skupno_values() \
            .values() 

class CenaQuerySet(models.QuerySet):
    def all_values(self):
        return self \
            .annotate(naziv = F("sestavina__naziv")) \
            .annotate(dimenzija = Coalesce(F("sestavina__dimenzija__dimenzija"),Value(""))) \
            .annotate(tip = Coalesce(F("sestavina__tip__dolgo"),Value(""))) \
            .values()
            
class SestavinaQuerySet(models.QuerySet):
    def zaloga_values(self, zaloga):
        return self \
        .annotate(zaloga=Sum(Case(
            When(vnoszaloge__zaloga=zaloga,then=F("vnoszaloge__stanje")),
            default=Value(0),
            output_field=IntegerField())))

    def vnosi_values(self,vnosi):
        return self \
            .annotate(vnesena = Exists(vnosi)) \
            .annotate(stevilo_vnosa=Coalesce(Subquery(vnosi.values("stevilo")[:1]),0))

    def cenik_values(self,zaloga):
        return self.annotate(cena=Sum(Case(
            When(cena__zaloga=zaloga,then=F("cena__cena")),
            default=Value(0.),
            output_field=FloatField())))

    def all_values(self):
        return self \
        .annotate(naziv_dimenzije = F("dimenzija__dimenzija")) \
        .annotate(kratek_tip = F("tip__kratko")) \
        .annotate(radij_dimenzije = F("dimenzija__radij")) \
        .values()

    def filtriraj(self,sestavina_filter):
        if sestavina_filter.radij != None:
            self.filter(dimenzija__radij=sestavina_filter.radij)
            if sestavina_filter.sirina != None:
                self.filter(dimenzija__sirina=sestavina_filter.sirina)
                if sestavina_filter.visina_special != None:
                    self.filter(dimenzija__visina_special = sestavina_filter.visina_special)
        return self.filter(tip__in=sestavina_filter.tipi)

class VnosZalogeQuerySet(models.QuerySet):
    def all_values(self):
        return self.annotate(dimenzija = F("sestavina__dimenzija__dimenzija")) \
            .annotate(tip = F("sestavina__tip__kratko")) \
            .values()
        
class VnosQuerySet(models.QuerySet):
    def all_values(self):
        return self.annotate(datum = F("baza__datum")) \
            .annotate(tip = F("baza__proxy_name")) \
            .annotate(status = F("baza__status")) \
            .annotate(sprememba_zaloge = F("baza__sprememba_zaloge")) \
            .annotate(title = F("baza__title")) \
            .order_by("datum","tip","sestavina") \
            .values()