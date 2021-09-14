class BazaModelElement extends ModelElement{
    constructor(){
        super();
    }

    connectedCallback(){
        super.connectedCallback();
        this.className = "Baza";
        this.filterAttr = "tip";
    }
    
}

window.customElements.define("baza-model-element",BazaModelElement);