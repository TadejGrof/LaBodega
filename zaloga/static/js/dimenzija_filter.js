const template = document.createElement('template');

template.innerHTML = `
    <style>

        #selectors{
            height:15%;
        }

        #selectors *{
            width:16%;
            height:100%;
            display:inline-block;
            text-align:center;
        }

        #buttons{
            height:85%;
        }

        button{
            width:32%;
            height:20%;
        }
    </style>

    <div id="filter">
        <div id="selectors">
            <div> Radij: </div>
            <select id="radij">
                <option value="all"> All </option>
            </select>
            <div> Sirina: </div>
            <select id="sirina">
                <option value="all"> All </option>
            </select>
            <div> Visina: </div>
            <select id="visina_special">
                <option value="all"> All </option>
            </select>
        </div>

        <div id="buttons">

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

    get event(){
        return new Event('final');
    }

    get dimenzija(){
        try{
            return this.filtrirajDimenzije[0];
        } catch(error){
            return null;
        }
    }

    set finalAction(action){
        this.addEventListener('final',action,false)
    }

    get radij(){
        return $("#radij",this.shadowRoot).val();
    }

    set radij(value){
        $("#radij",this.shadowRoot).val(value);
        this.setAttribute("radij",value);
    }

    get sirina(){
        return $("#sirina",this.shadowRoot).val();
    }

    set sirina(value){
        $("#sirina",this.shadowRoot).val(value);
        this.setAttribute("sirina",value);
    }

    get visina_special(){
        return $("#visina_special",this.shadowRoot).val();
    }

    set visina_special(value){
        $("#visina_special",this.shadowRoot).val(value);
        this.setAttribute("visina_special",value);
    }

    static get observedAttributes(){    
        return ["radij","sirina","visina_special"];
    }

    attributeChangedCallback(name,oldValue,newValue){
        if(name == "radij"){
            this.clearSelector("sirina");
            this.clearSelector("visina_special");
            if(newValue!="all"){
                this.setRazlicni(this.filtrirajDimenzije,"sirina");
            }
        } else if(name == "sirina"){
            this.clearSelector("visina_special");
            if(newValue != "all"){
                this.setRazlicni(this.filtrirajDimenzije,"visina_special");
            }
        } else if(name = "visina_special"){
            if(newValue != "all"){
                this.dispatchEvent(this.event); 
            }
        }
        this.nastaviGumbe();
    }

    connectedCallback(){
        var filter = this;
        $("select",this.shadowRoot).change(function(){
            filter.setAttribute(this.id, $(this).val());
        });
        this.nastaviGumbe();
        this.visina_special = "all";
    }

    disconnectedCallback(){
        $("select",this.shadowRoot).unbind();
    }

    clear(){
        this.radij = "all";
    }

    get filter(){
        for(var f of DimenzijaFilter.observedAttributes){
            if(this.getAttribute(f) == "all" || this.getAttribute(f) == null) return f;
        }
        return null;
    }

    nastaviGumbe(){
        var buttons = this.shadowRoot.querySelector("#buttons");
        var dimenzijaFilter = this;
        var filter = this.filter;
        buttons.innerHTML = "";
        if(filter == null) return;
        var selector = this.shadowRoot.querySelector("#" + filter);
        $(".data",selector).each(function() {
            var button = document.createElement("button");
            var value = this.text;
            button.innerHTML = this.text;
            $(button).click(function(){
                $("#" + filter ,dimenzijaFilter.shadowRoot).val(value);
                dimenzijaFilter.setAttribute(filter,value);
            });
            $(buttons).append(button);
        });
    };

    get filtrirajDimenzije(){
        var filtri = []
        if (this.radij != "all"){ filtri.push("radij")};
        if (this.sirina != "all"){ filtri.push("sirina")};
        if (this.visina_special != "all"){ filtri.push("visina_special")};
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

}

window.customElements.define("dimenzija-filter",DimenzijaFilter);
