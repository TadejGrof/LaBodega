from django.db import models
from django.db.models import IntegerField,FloatField,CharField
from django.db.models import F,Value,Subquery, Count, OuterRef, Sum, When, Case, Q, Exists
from django.db.models.functions import Concat,Cast, Coalesce, Round

class ModelQuerySet(models.QuerySet):
    def all_values(self):
        return self.values()

        