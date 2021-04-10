from django.urls import include,path
from .import views

urlpatterns = [
    path('dimenzije/',views.dimenzije,name="dimenzije"),
    path('authenticate/',views.authenticate,name="authenticate"),
    path('get_csrf/',views.get_csrf,name="get_csrf")
]