from rest_framework import serializers
from .models import *
import datetime

class PodjetjeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Podjetje
        fields = ["title"]

class PoslovnaEnotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PoslovnaEnota
        fields = "__all__"
        depth = 1

class VnosBazeSerializer(serializers.ModelSerializer):
    baza = serializers.PrimaryKeyRelatedField(queryset=Baza.objects.all())
    sestavina = serializers.PrimaryKeyRelatedField(queryset=Sestavina.objects.all())
    paket = serializers.PrimaryKeyRelatedField(queryset=VnosTipaPaketa.objects.all(), required=False)
    lastnostSestavine = serializers.PrimaryKeyRelatedField(queryset=LastnostSestavine.objects.all(), required=False)
    
    class Meta:
        model = VnosBaze
        fields = "__all__"

class BazaSerializer(serializers.ModelSerializer):
    zaloga = serializers.PrimaryKeyRelatedField(queryset=Zaloga.objects.all())

    class Meta:
        model = Baza
        fields = ["vnosi","zaloga"]
        depth = 1

class DimenzijaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dimenzija
        fields = "__all__"

class TipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tip
        fields = "__all__"
        
class SestavinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sestavina
        fields = "__all__"