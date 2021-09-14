from django import template
import json as JSON
import datetime 
from decimal import Decimal

register = template.Library()

@register.filter(name="ima_prodajo")
def ima_prodajo(zaloga,prodaja):
    return prodaja in zaloga.tipi_prodaj
    
@register.filter(name="ima_aktivno_bazo")
def ima_aktivno_bazo(stranka,zaloga):
    return stranka.ima_aktivno_prodajo(zaloga)

@register.filter(name='index')
def razlika(value, index):
    return value[index] 

@register.filter
def jsonList(data):
    print(data)
    seznam = [clear_data(x) for x in data]
    return JSON.dumps(seznam)

def clear_data(data):
    for key, value in data.items():
        if(isinstance(value,list)):
            data[key] = JSON.loads(jsonList(value))
        if isinstance(value,(datetime.date,datetime.datetime)):
            data[key] = str(value)
        elif isinstance(value,Decimal):
            data[key] = float(value)
    return data

@register.filter
def json(data):
    return JSON.dumps(clear_data(data))

@register.filter
def zadnji(list):
    return list[-1] 

@register.filter
def datum(datetime):
    return datetime.date()

@register.filter
def datum_str(date):
    return date.strftime('%Y-%m-%d')

@register.filter
def getDayOfWeek(datum):
    dnevi = ["Ponedeljek","Torek","Sreda","Četrtek","Petek","Sobota","Nedelja"]
    return dnevi[datum.weekday()]

@register.filter
def split(string,locilo):
    return string.split(locilo)

@register.filter
def odstrani(seznam, element):
    if isinstance(seznam,str):
        seznam = JSON.loads(seznam)
    else:
        seznam = seznam
    for x in seznam:
        if x == element:
            seznam.remove(element)
    return JSON.dumps(seznam)

@register.filter
def dodaj(seznam, element):
    if isinstance(seznam,str):
        seznam = JSON.loads(seznam)
    else:
        seznam = seznam
    seznam.append(element)
    return JSON.dumps(seznam)

@register.filter
def divide(value, arg):
    try:
        return int(value) / int(arg)
    except (ValueError, ZeroDivisionError):
        return None

@register.filter
def dolgi_tip(zaloga, tip):
    for seznam_tipa in zaloga.vrni_tipe:
        if seznam_tipa[0] == tip:
            return seznam_tipa[1]

@register.filter(name='razlika')
def razlika(value, arg):
    if value == None:
        return "/"
    return value - arg 

@register.filter(name='dimenzija')
def razlika(dimenzije, pk):
    for dimenzija in dimenzije:
        if dimenzija['pk'] == pk:
            return dimenzija['dimenzija']

@register.filter(name='zaloga')
def razlika(sestavina, tip):
    return sestavina[tip]

@register.filter(name='prijazna_dimenzija')
def kj_none(value):
    return value.replace('/','-')

@register.filter(name='replace')
def replace(value):
    if '/' in value:
        return value.replace('/','-')
    else:
        return value.replace('-','/')
    
@register.filter(name='skupno')
def skupno(baza,tip):
    skupno = 0
    for vnos in baza.vnos_set.all():
        if tip == "all":
            skupno += vnos.stevilo
        elif tip == vnos.tip:
            skupno += vnos.stevilo
    return skupno

@register.filter
def keyvalue(dict, key):   
    return dict[key]

@register.filter
def stringvalue(obj, string):   
    return getattr(obj,string)

@register.filter
def split(obj, split_value):   
    return obj.split(split_value)


@register.filter(name='tip')
def tip(value, arg):
    if int(arg) == 0:
        return value.yellow
    elif int(arg) == 1:
        return value.white