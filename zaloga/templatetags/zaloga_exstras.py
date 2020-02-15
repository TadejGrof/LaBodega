from django import template

register = template.Library()

@register.filter(name='index')
def razlika(value, index):
    return value[index] 

@register.filter
def zadnji(list):
    return list[-1] 

#vele_prodaja.html
@register.filter
def skupna_cena(vnos):
    return vnos['stevilo'] * vnos['cena']

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