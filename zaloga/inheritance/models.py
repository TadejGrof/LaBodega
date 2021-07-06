import sys
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class ProxySuper(models.Model):
    class Meta:
        abstract = True

    proxy_name = models.CharField(max_length=20)

    @property
    def tip(self):
        return self.proxy_name

    @classmethod
    def get_class(cls, class_name):
        try:
            return getattr(sys.modules[cls.__module__], class_name)
        except:  
            try:
                return getattr(sys.modelus[cls.__module__], class_name[0].upper() + class_name[1:])
            except:
                return None

    @classmethod
    def create(cls, klas, *args, **kwargs):
        try:
            return klas.objects.create(*args,**kwargs)
        except:
            return cls.get_class(klas).objects.create(*args,**kwargs)

    def save(self, *args, **kwargs):
        """ automatically store the proxy class name in the database """
        self.proxy_name = type(self).__name__
        super().save(*args, **kwargs)

    def __new__(cls, *args, **kwargs):
        """ create an instance corresponding to the proxy_name """
        proxy_class = cls
        try:
            field_name = ProxySuper._meta.get_fields()[0].name
            proxy_name = kwargs.get(field_name)
            if proxy_name is None:
                proxy_name_field_index = cls._meta.fields.index(
                    cls._meta.get_field(field_name))
                proxy_name = args[proxy_name_field_index]
            proxy_class = getattr(sys.modules[cls.__module__], proxy_name)
        finally:
            return super().__new__(proxy_class)

class ProxyManager(models.Manager):
    def get_queryset(self):
        """ only include objects in queryset matching current proxy class """
        return self.queryset().filter(proxy_name=self.model.__name__)

    def queryset(self,queryset=None):
        if queryset == None:
            queryset = super().get_queryset()
        return queryset

