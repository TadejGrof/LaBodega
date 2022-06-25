from django.db import models
from django.db.models.functions import Coalesce

class BazaQuerySet(models.QuerySet):
    def skupna_baza(self):
        from .models import Baza
        return Baza()