from django.db import models


# Create your models here.

class Podjetje(models.Model):
    naziv = models.CharField(default="/",max_length=50)

class PoslovnaEnota(models.Model):
    naziv = models.CharField(default="/",max_length=50)
    podjetje = models.ForeignKey(Podjetje,on_delete=models.CASCADE)
    
class Tip(models.Model):
    naziv = models.CharField(default="/",max_length=30)
    kratica = models.CharField(default="/",max_length=5)
    barva = models.CharField(default="yellow",max_length=30)

class Dimenzija(models.Model):
    radij = models.CharField(default="/",max_length=30)
    sirina = models.CharField(default="/",max_length=30)
    visina = models.CharField(default="/",max_length=30)
    special = models.BooleanField(default=False)
    dimenzija = models.CharField(default="/",max_length=30)

    class Meta:
        ordering = ['radij', 'visina', 'sirina' , 'special']

    def __str__(self):
        return self.dimenzija
    
class Sestavina(models.Model):
    naziv = models.CharField(default="/",max_length=30)
    dimenzija = models.ForeignKey(Dimenzija,default=None,blank=True, null=True,on_delete=models.CASCADE)
    tip = models.ForeignKey(Tip,default=None,blank=True, null=True,on_delete=models.CASCADE)
    lastnosti = models.ManyToManyField("LastnostSestavine")

    def __str__(self):
        return self.naziv

class LastnostSestavine(models.Model):
    naziv = models.CharField(default="TRDOTA", max_length=30)

class Zaloga(models.Model):
    naziv = models.CharField(default="/",max_length=30)
    poslovnaEnota = models.ForeignKey(PoslovnaEnota, on_delete=models.CASCADE)

    def __str__(self):
        return self.naziv

class VnosZaloge(models.Model):
    zaloga = models.ForeignKey(Zaloga,on_delete=models.CASCADE, related_name="vnosi")
    sestavina = models.ForeignKey(Sestavina, on_delete=models.CASCADE, related_name="vnosi_zaloge")
    lastnostSestavine = models.ForeignKey(LastnostSestavine,on_delete=models.SET_NULL, default=None, null=True, blank=True, related_name="vnosi_zaloge")
    kolicina = models.FloatField(default=0)

class Baza(models.Model):
    zaloga = models.ForeignKey(Zaloga,default=None,null=True,blank=True,on_delete=models.SET_NULL)
    naziv = models.CharField(default="/",max_length=30)
    tip = models.CharField(default="/",max_length=30)
    status = models.CharField(default="aktivno",max_length=30)
    datum = models.DateTimeField()

    def uveljavi(self):
        self.status = "veljavno"
        self.save()
        print("UVELJAVLJAM BAZO")

class Paket(models.Model):
    baza = models.ForeignKey(Baza,default=None, null=True, blank=True, on_delete=models.SET_NULL)
    cas = models.DateTimeField()
    isModel = models.BooleanField(default=False)

class VnosDimenzijePaketa(models.Model):
    paket = models.ForeignKey(Paket, on_delete=models.CASCADE)
    dimenzija = models.ForeignKey(Dimenzija, on_delete=models.CASCADE)

class VnosTipaPaketa(models.Model):
    vnosDimenzijePaketa = models.ForeignKey(VnosDimenzijePaketa, on_delete=models.CASCADE)
    tip = models.ForeignKey(Tip,default=None,null=True,blank=True,on_delete=models.SET_NULL)
    lastnostSestavine = models.ForeignKey
    kolicina = models.IntegerField(default=0)

class VnosBaze(models.Model):
    baza = models.ForeignKey(Baza,on_delete=models.CASCADE, related_name="vnosi")
    sestavina = models.ForeignKey(Sestavina,on_delete=models.CASCADE)
    lastnostSestavine = models.ForeignKey(LastnostSestavine, on_delete=models.SET_NULL, default=None, null=True, blank=True)
    stevilo = models.IntegerField(default=0)
    # NASTAVLJENO ZA BAZE TIPA KONTEJNER
    paket = models.OneToOneField(VnosTipaPaketa,default=None, null=True,blank=True, on_delete=models.CASCADE)
    cas = models.DateTimeField(default=None, null=True,blank=True)

class SpremembaZaloge(models.Model):
    vnos_baze = models.ForeignKey(VnosBaze, on_delete=models.CASCADE)
    vnos_zaloge = models.ForeignKey(VnosZaloge,on_delete=models.CASCADE)
    sprememba = models.FloatField()
    fiks = models.BooleanField(default=False)
    cas = models.DateTimeField()