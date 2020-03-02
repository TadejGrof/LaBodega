function Confirm() {
    if (!confirm('are you sure?')){
        return false
    } else{
        return true
    }
}
function toggle(className, displayState){
    var elements = document.getElementsByClassName(className)
    for (var i = 0; i < elements.length; i++){
        elements[i].style.display = displayState;
    }
}; 
function ToggleClass(selector, className){
    $(selector).toggleClass(className)
}
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
    var element = document.getElementById(id)
    if (element){
        return element.value
    }
    return null
}
function set_value(id, value){
    var element = document.getElementById(id)
    if (element){
        element.value = value
    }
}
function get_innerHtml(id){
    var element = document.getElementById(id)
    if (element){
        return element.innerHTML
    }
}
function set_innerHtml(id, html){
    var element = document.getElementById(id)
    if (element){
        element.innerHTML = html
    }
}
function add_class(elements,klas){
    for (var i = 0; i < elements.length; i++) {
        elements[i].classList.add(klas)
    }
}
function remove_class(elements,klas){
    for (var i = 0; i < elements.length; i++) {
        elements[i].classList.remove(klas)
    }
}
function set_placeholder(id, placeholder){
    document.getElementById(id).placeholder = placeholder; 
}
function get_selected(id){
    var box = document.getElementById(id)
    if (box){
        return box.options[box.selectedIndex].value
    }
    return null
}
function set_selected(id, index){
    var box = document.getElementById(id)
    if (box){
        box.selectedIndex = index
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