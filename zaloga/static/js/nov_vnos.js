const novVnosTemplate = document.createElement('template');

novVnosTemplate.innerHTML = `
        <style>
            div.toggle{
                height:4vh;
                margin-bottom:3%;
            }
            div.nov_vnos{
                height:auto;
            }
            div.gumbi{
                height:20vh;
            }
            div.toggle button{
                width:49%;
                display:inline-block;
                margin:0%;
                padding:0%;
                height:100%;
            }
        </style>

        <div class="nov_vnos">
            <div class="toggle">
                <button class="tabela"> Tabela </button>
                <button class="gumbi"> Gumbi </button>
            </div>
            <div class="tabela">
                <dimenzija-dinamic-filter></dimenzija-dinamic-filter>
            </div>
            <div class="gumbi skrit">
                <dimenzija-filter class="filter_tip">
                </dimenzija-filter>
                <div class="koncno">
                </div>
            </div>
            

            
        <div>
    `;

class NovVnos extends HTMLElement{
    constructor(){
        super();
        this.append(novVnosTemplate.content.cloneNode(true));
    }
   
    get event(){
        return new Event('final');
    }

    static get observedAttributes(){    
        return ["vnos"];
    }

    get vnos(){
        return JSON.parse(this.getAttribute("vnos"));
    }

    set vnos(data){
        this.setAttribute("vnos",JSON.stringify(data));
    }

    set finalAction(action){
        this.addEventListener('final',action,false)
    }

    attributeChangedCallback(name,oldValue,newValue){
        if(name=="vnos"){
            this.dispatchEvent(this.event);
        }
    }

    connectedCallback(){
        var nov_vnos = this;
        $("div.toggle button.tabela",this).click(function(){
            $("div.tabela",nov_vnos).removeClass("skrit");
            $("div.gumbi",nov_vnos).addClass("skrit");
        });
        $("div.toggle button.gumbi",this).click(function(){
            $("div.tabela",nov_vnos).addClass("skrit");
            $("div.gumbi",nov_vnos).removeClass("skrit");
        });

        this.querySelector("dimenzija-dinamic-filter").finalAction = function(){
            if(this.vnos != null){
                nov_vnos.vnos = this.vnos;
            }
        };

        var koncno = this.querySelector("div.koncno");
        
        this.querySelector("dimenzija-filter").finalAction = function(){
            var dimenzija = this.dimenzija;
            $(koncno).removeClass("skrit");
            $(this).addClass("skrit");
            $(".dimenzija",koncno).html(dimenzija);
        };

    }
}

window.customElements.define("nov-vnos",NovVnos);
