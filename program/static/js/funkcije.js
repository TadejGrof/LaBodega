function toggle(className, displayState){
    var elements = document.getElementsByClassName(className)
    for (var i = 0; i < elements.length; i++){
        elements[i].style.display = displayState;
    }
}; 
function barva(className, color){
    var elements = document.getElementsByClassName(className)
    for (var i = 0; i < elements.length; i++){
        elements[i].style.backgroundColor = color
    }
}
function set_id(id1,id2){
    document.getElementById(id1).id = id2
}
function get_value(id){
    return document.getElementById(id).value
}
function set_value(id, value){
    document.getElementById(id).value = value
}
function get_innerHtml(id){
    return document.getElementById(id).innerHTML
}
function set_innerHtml(id, html){
    document.getElementById(id).innerHTML = html
}
function je_veljavno_stevilo(stevilo){
    if (! stevilo == ""){
        return true
    }
}
function je_veljavna_cena(cena){
    val = parseFloat(cena)
    if (! cena == "" && !isNaN(val)){
        return true
    } else{
        return false
    }
}
function je_veljaven_popust(popust){
    if (! popust == ""){
        return true
    }
}
function je_prazno(id){
    if (document.getElementById(id).value == ""){
        return true
    } else{
        return false
    }
};
function skrij(id){
    document.getElementById(id).style.display = "none"
};
function pokazi_block(id){
    document.getElementById(id).style.display = "block"
};
function pokazi_inline_block(id){
    document.getElementById(id).style.display = "inline-block"
};
function Skrij(id){
    document.getElementById(id).style.visibility = 'hidden'
};
function razkrij(id){
    document.getElementById(id).style.visibility = "visible"
};