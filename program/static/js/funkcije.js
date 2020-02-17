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