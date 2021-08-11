const template = document.createElement('template');

template.innerHTML = `
    <style>
        .selectors{
            height:20%;
        }

        .button{
            height:80%;
        }
    </style>

    <div class="filter">
        <div class="selectors">
            Radij:
            <select id="radij">
                <option value="all"> All </option>
            </select>
            Sirina:
            <select id="sirina">
                <option value="all"> All </option>
            </select>
            Visina:
            <select id="visinaSpecial">
                <option value="all"> All </option>
            </select>
        </div>

        <div class="buttons">

        </div>
    </div>
    `;

class DimenzijaFilter extends HTMLElement{

    constructor(){
        super();
        this.attachShadow({mode:"open"});
        this.shadowRoot.appendChild(template.content.cloneNode(true));
        this.setRazlicni(dimenzije,"radij");
    }

    get radij(){
        return $("#radij",this.shadowRoot).val();
    }

    get sirina(){
        return $("#sirina",this.shadowRoot).val();
    }

    get visinaSpecial(){
        return $("#visinaSpecial",this.shadowRoot).val();
    }

    static get observedAttributes(){
        return ["radij","sirina","visinaSpecial"];
    }

    attributeChangedCallback(name,oldValue,newValue){
        if(name == "radij"){
            this.clearSelector("sirina");
            this.clearSelector("visinaSpecial");
            if(newValue!="all"){
                alert(this.filtrirajDimenzije);
                this.setRazlicni(this.filtrirajDimenzije,"sirina");
            }
        } else if(name == "sirina"){
            this.clearSelector("visinaSpecial");
            if(newValue != "all"){
                this.setRazlicni(this.filtrirajDimenzije,"visinaSpecial");
            }
        }

    }

    connectedCallback(){
        var filter = this;
        $("select",this.shadowRoot).change(function(){
            filter.setAttribute(this.id, $(this).val());
        });
    }

    disconnectedCallback(){

    }

    nastaviGumbe(){

    };

    get filtrirajDimenzije(){
        var filtri = []
        if (this.radij != "all"){ filtri.push("radij")};
        if (this.sirina != "all"){ filtri.push("sirina")};
        if (this.visinaSpecial != "all"){ filtri.push("visinaSpecial")};
        var filtrirane = []
        for(var dimenzija of dimenzije){
            var veljavno = true;
            for(var filter of filtri){
                if(this.getAttribute(filter) != dimenzija[filter]){
                    veljavno = false;
                    break;
                }
            }
            if ( veljavno ) filtrirane.push(dimenzija);
        }
        return filtrirane;
    }

    clearSelector(id){
        $("#" + id, this.shadowRoot).find(".data").remove();
    }

    setRazlicni(dimenzije, id){
        this.clearSelector(id);
        var razlicni = [];
        var select = this.shadowRoot.querySelector('#' + id);
        for(var dimenzija of dimenzije){
            var data = dimenzija[id];
            if(!razlicni.includes(data)){
                razlicni.push(data);
            }
        }
        razlicni.sort();
        for(var data of razlicni){
            var option = document.createElement("option");
            option.text = data;
            option.value = data;
            option.classList.add("data");
            select.add(option);
        }
    }

    spremeni_radij(){

    }
}

window.customElements.define("dimenzija-filter",DimenzijaFilter);
