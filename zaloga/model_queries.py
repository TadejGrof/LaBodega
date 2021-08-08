from django.db import models
from django.db.models import IntegerField,FloatField,CharField
from django.db.models import F,Value,Subquery, Count, OuterRef, Sum, When, Case, Q, Exists
from django.db.models.functions import Concat,Cast, Coalesce, Round
from program.model_queries import ModelQuerySet

class BazaQuerySet(ModelQuerySet):
    def aktivne_baze(self, tip, zaloga):
        return self.filter(zaloga=zaloga,tip=tip, status="aktivno")

    def cakajoce_baze(self,tip, zaloga):
        return self.filter(zaloga=zaloga,tip=tip, status="cakajoce")

    def author_values(self):
        return self \
        .annotate(username_creatorja = F("author__username")) \
        .annotate(username_uveljavitelja = F("author__username"))

    def dobavitelj_values(self):
        return self \
        .annotate(naziv_dobavitelja = Coalesce(F("dobavitelj__podjetje__naziv"),Value(""))) \
        .annotate(drzava_dobavitelja = Coalesce(F("dobavitelj__podjetje__drzava__naziv"),Value(""))) 
        #.annotate(telefon_dobavitelja = Coalesce(F("dobavitelj__telefon"),Value(""))) \
        #.annotate(email_dobavitelja = Coalesce(F("dobavitelj__mail"),Value(""))) \
        #.annotate(ulica_dobavitelja = Coalesce(F("dobavitelj__ulica"),Value(""))) \
        #.annotate(status_dobavitelja = Coalesce(F("dobavitelj__status"),Value(""))) \
        #.annotate(davcna_dobavitelja = Coalesce(F("dobavitelj__davcna"),Value(""))) 

    def stranka_values(self):
        return self \
        .annotate(naziv_stranke = Coalesce(F("stranka__naziv"),Value(""))) \
        .annotate(telefon_stranke = Coalesce(F("stranka__telefon"),Value(""))) \
        .annotate(email_stranke = Coalesce(F("stranka__mail"),Value(""))) \
        .annotate(ime_stranke = Coalesce(F("stranka__ime"),Value(""))) \
        .annotate(status_stranke = Coalesce(F("stranka__status"),Value(""))) \
        .annotate(davcna_stranke = Coalesce(F("stranka__davcna"),Value("")))
        #.annotate(ulica_stranke = Coalesce(F("stranka__ulica"),Value(""))) \

    def skupno_values(self):
        return self \
        .annotate(skupno_stevilo = Coalesce(Sum("vnos__stevilo"),0)) \
        .annotate(skupna_cena = Coalesce(Sum(F("vnos__stevilo") * Coalesce(F("vnos__cena"),0), output_field=FloatField()),0)) \
        .annotate(skupna_cena_nakupa = Sum(F("vnos__stevilo") * Coalesce(F("vnos__cena_nakupa"),0), output_field=FloatField())) \
        .annotate(razlika = F("skupna_cena") - F("skupna_cena_nakupa")) \
        .annotate(cena_popusta = Round(F("skupna_cena") * Coalesce(F("popust"),0) / Value(100), output_field=FloatField())) \
        .annotate(cena_prevoza = Round(F("skupno_stevilo") * Coalesce(F("prevoz"),0), output_field=FloatField())) \
        .annotate(koncna_cena = F("skupna_cena") - F("cena_popusta") + F("cena_prevoza")) \
        .annotate(dolg = Coalesce(Cast(F("koncna_cena") - F("placilo"),FloatField()),0)) \

    def all_values(self):
        return self \
            .annotate(stevilka_kontejnerja = Coalesce(F("kontejner__stevilka"),Value(""))) \
            .annotate(ladijski_prevoz_value = Coalesce(F("ladijski_prevoz"),0)) \
            .dobavitelj_values() \
            .stranka_values() \
            .author_values() \
            .skupno_values() \
            .values() 

class DobaviteljQuerySet(ModelQuerySet):
    def all_values(self):
        return self \
            .annotate(naziv=F("podjetje__naziv")) \
            .values()

class CenaQuerySet(ModelQuerySet):
    def all_values(self):
        return self \
            .annotate(naziv = F("sestavina__naziv")) \
            .annotate(dimenzija = Coalesce(F("sestavina__dimenzija__dimenzija"),Value(""))) \
            .annotate(tip = Coalesce(F("sestavina__tip__dolgo"),Value(""))) \
            .values()
            
class SestavinaQuerySet(ModelQuerySet):
    def zaloga_values(self, zaloga):
        return self \
        .annotate(stanje=Sum(Case(
            When(vnoszaloge__zaloga=zaloga,then=F("vnoszaloge__stanje")),
            default=Value(0),
            output_field=IntegerField())))

    def vnosi_values(self,vnosi):
        return self \
            .annotate(vnesena = Exists(vnosi)) \
            .annotate(stevilo_vnosa=Coalesce(Subquery(vnosi.values("stevilo")[:1]),0)) \
            .annotate(pk_vnosa = Coalesce(Subquery(vnosi.values("pk")[:1]),0))

    def cenik_values(self,zaloga):
        return self.annotate(cena=Sum(Case(
            When(cena__zaloga=zaloga,then=F("cena__cena")),
            default=Value(0.),
            output_field=FloatField())))

    def all_values(self):
        return self \
        .annotate(naziv_dimenzije = F("dimenzija__dimenzija")) \
        .annotate(kratek_tip = F("tip__kratko")) \
        .annotate(radij_dimenzije = F("dimenzija__radius")) \
        .values()

    def filtriraj(self,sestavina_filter):
        if sestavina_filter.radij != None:
            self.filter(dimenzija__radij=sestavina_filter.radij)
            if sestavina_filter.sirina != None:
                self.filter(dimenzija__sirina=sestavina_filter.sirina)
                if sestavina_filter.visina_special != None:
                    self.filter(dimenzija__visina_special = sestavina_filter.visina_special)
        return self.filter(tip__in=sestavina_filter.tipi)

class VnosZalogeQuerySet(ModelQuerySet):
    def all_values(self):
        return self.annotate(dimenzija = F("sestavina__dimenzija__dimenzija")) \
            .annotate(tip = F("sestavina__tip__kratko")) \
            .annotate(dimenzija_id = F("sestavina__dimenzija__id")) \
            .annotate(tip_id = F("sestavina__tip__id")) \
            .values()

class VnosQuerySet(ModelQuerySet):
    use_for_related_fields = True

    def all_values(self):
        values =  self.annotate(datum = F("baza__datum")) \
            .annotate(status = F("baza__status")) \
            .annotate(tip_baze = F("baza__tip")) \
            .annotate(title_baze = F("baza__title")) \
            .annotate(sprememba_zaloge = F("baza__sprememba_zaloge")) \
            .annotate(title = F("baza__title")) \
            .annotate(radij = F("sestavina__dimenzija__radius")) \
            .annotate(dimenzija = F("sestavina__dimenzija__dimenzija")) \
            .annotate(dimenzija_id = F("sestavina__dimenzija__id")) \
            .annotate(tip = F("sestavina__tip__kratko")) \
            .annotate(dolgi_tip = F("sestavina__tip__dolgo")) \
            .annotate(tip_id = F("sestavina__tip__id")) \
            .annotate(skupna_cena=Coalesce(Cast(F("stevilo") * F("cena"), FloatField()),0)) \
            .order_by("sestavina") \
            .values()
        i = 0
        for value in values:
            value["index"] = i
            i += 1
        return values