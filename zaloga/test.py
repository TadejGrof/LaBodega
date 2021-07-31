from .models import Dnevna_prodaja, Zaloga, Sestavina, Baza, Sprememba, Cena, Vnos
import json
from django.db.models import F, IntegerField,Value
from django.db.models.functions import Concat


