from django.urls import include,path
from .import views

urlpatterns = [
    path('dimenzije/',views.dimenzije,name="dimenzije"),
]