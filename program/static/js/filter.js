function Tip_button(tip){
    toggle('vrstica','none');
    toggle('vrstica_' + tip,'block')
};
function Uredi(){
    toggle('uredi','inline-block');
    toggle('uredi_gumb','none');
};
function Preklici_urejanje(){
    toggle('uredi','none');
    toggle('uredi_gumb','inline-block');
};
function Spremeni_popust(){
    toggle('spremeni_popust','none')
    toggle('potrdi_popust','inline-block')
};
function Preklici_spremembo_popusta(){
    toggle('spremeni_popust','inline-block')
    toggle('potrdi_popust','none')
};
function Spremeni_prevoz(){
    toggle('spremeni_prevoz','none')
    toggle('potrdi_prevoz','inline-block')
};
function Preklici_spremembo_prevoza(){
    toggle('spremeni_prevoz','inline-block')
    toggle('potrdi_prevoz','none')
};
function Spremeni_vnos(pk){
    toggle('spremeni_' + pk, 'none');
    toggle('potrdi_' + pk, 'inline-block')
};
function Preklici_spremembo_vnosa(pk){
    toggle('spremeni_' + pk, 'inline-block');
    toggle('potrdi_' + pk, 'none')
}
function Nov_vnos(){
    Preklici_urejanje();
    toggle('pre_nov_vnos','none');
    toggle('nov_vnos','inline-block');
}
function Preklici_nov_vnos(){
    toggle('pre_nov_vnos','inline-block');
    toggle('nov_vnos','none');
}
