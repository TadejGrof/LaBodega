const dimenzijaDinamicFilterRowTemplate = document.createElement('template');


const dimenzijaDinamicFilterTemplate = document.createElement('template');

dimenzijaDinamicFilterTemplate.innerHTML = `
    <style>
        div.table table.dinamic_filter th{
            width:25%;
        }
        table.dinamic_filter button, table.dinamic_filter input, table.dinamic_filter select{
            width:70%;
        }
    </style>
    <div class="dimenzijaDinamicFilter">
        <div class="filter">
            Filtriraj:
            <input type="text" class="filter"> </input>
        </div>
        <div class="table">
            <table class="dinamic_filter tabela_vnosov">
                <tr class="header">
                    <th class="dimenzija"> Dimenzija: </th>
                    <th class="tip"> Tip: </th>
                    <th class="stevilo"> Stevilo: </th>
                    <th class="edit"> Dodaj: </th>
                </tr>
            </table>
        </div>
    </div>
    `   

class DimenzijaDinamicFilter extends HTMLElement{

    constructor(){
        super();
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

    attributeChangedCallback(name,oldValue,newValue){
        if(name=="vnos"){
            this.dispatchEvent(this.event);
        }
    }

    set finalAction(action){
        this.addEventListener('final',action,false)
    }

    focus(){
        $("input.filter",this).focus();
    }

    connectedCallback(){
        this.append(dimenzijaDinamicFilterTemplate.content.cloneNode(true));
        var filter = this;
        $("input.filter",this).on('input',function(){
            filter.filtriraj();
        });

        window.addEventListener("keydown",function (e) {
            if(e.ctrlKey && e.keyCode == 70){
                if($(filter).is(":visible")){
                    e.preventDefault();
                    filter.focus();
                }
            }
        });
    }

    set finalAction(action){
        this.addEventListener('final',action,false)
    }

    filterStatus(filter){
        if(filter.length == 3){
            return "sirina";
        } else if(filter.length == 2){
            if(filter.charAt(0) == "1" || filter.charAt(0) == "2"){
                return "radij";
            } 
            return "visina_special";
        }
        return null;
    };

    filtriraj(){
        $('vnos-model-element', this).remove();
        var filtrirane = this.filtriraneDimenzije;
        var i = 0;
        for(var dimenzija of filtrirane){
            if (i > 10) break;
            i++;
            var model = document.createElement("vnos-model-element");
            model.parent = $(this).closest(".modelElement[className='Baza']").get(0).id;
            $('tbody',this).append(model);
            $("[attrName='dimenzija']",model).get(0).value = dimenzija["dimenzija"];
            model.removeIndex();
            model.parent.refresh();
        }
    }

    get filtriraneDimenzije(){
        var filter = $('input.filter',this).val();
        var filtri = filter.split(/ |,|;|\/|,/);
        var filtrirane = dimenzije;
        for(var filter of filtri){
            filter = filter.replace("R","")
            var status = this.filterStatus(filter)
            if(status != null){
                var pravilne = [];
                for(var dimenzija of filtrirane){
                    var value = dimenzija[status];
                    value = value.toString();
                    if(dimenzija[status].toString().includes(filter)){
                        pravilne.push(dimenzija);
                    };
                }
                filtrirane = pravilne;
            }
        }
        return filtrirane;

    }

}

window.customElements.define("dimenzija-dinamic-filter",DimenzijaDinamicFilter);
