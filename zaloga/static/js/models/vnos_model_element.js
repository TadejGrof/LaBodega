var vnosModelTemplate = document.createElement("template");

vnosModelTemplate.innerHTML = `
    <style>
        vnos-model-element{
            display: table-row;
        }
    </style>

    <td class="index">
        <index-element search="vnos-model-element"> </index-element>
    </td>
    <td>
        <value-element attrName="dimenzija"> </value-element>
    </td>
    <td>
        <model-select-value-element attrName="sestavina__tip" textAttr="kratko"> </model-select-value-element>
    </td>
    <td>
        <input-value-element type="number" attrName="stevilo"> </input-value-element>
    </td>
    <td filter="vele_prodaja">
        <value-element attrName="narocilo" filter="vele_prodaja"> </value-element>
    </td>
    <td filter="vele_prodaja">
        <input-value-element type="price" attrName="cena" filter="vele_prodaja"> </input-value-element>
    </td>
    <td filter="vele_prodaja">
        <value-element type="price" attrName="skupna_cena" filter="vele_prodaja"> </value-element>
    </td>
    <td>
        <div class="edit" hidden="hidden">
            <div class="sprememba">
                <button is="toggle-button" toggle=".sprememba" scope="vnos-model-element"> E </button>
                <button is="delete-button" scope="vnos-mode-element"> X </button>    
            </div>
            <div class="skrit sprememba">
                <button is="save-button"> Ok </button>
                <button is="toggle-button" toggle=".sprememba" scope="vnos-model-element"> <- </button>
            </div>
            </div>
        <div class="create">
            <button is="create-button"> Ok </button>
        </div>
    </td>
`

class VnosModelElement extends ModelElement{
    constructor(){
        super();
    }

    refresh(){
        super.refresh();
        $("index-element",this).get(0).refresh();
    }

    connectedCallback(){
        super.connectedCallback();
        this.append(vnosModelTemplate.content.cloneNode(true));
        $(".valueElement[attrName='sestavina__tip']",this).get(0).options = tipi;
        this.className = "Vnos";
        this.classList.add("vnosModelElement");
        this.parentAttr = "baza";
        this.filterAttr = "tip";
    }

    modelChange(model){
        super.modelChange(model);
        if(model == null){
            $("div.edit",this).hide();
            $("div.create",this).show();
        } else {
            $("div.edit",this).show();
            $("div.create",this).hide();
        }
    }

    getFilterAttr(){
        return this.parent.model[this.filterAttr]; 
    }

    removeIndex(){
        $(".index",this).remove();
    }

    postSave(data, includeParent){
        this.parent.model = data["parent"];
    };

    getSestavina(){
        var dimenzija = $("[attrName='dimenzija']",this).get(0).value;
        var tip = $("[attrName='sestavina__tip']",this).get(0).value
        for(var sestavina of sestavine){
            if(sestavina["naziv_dimenzije"] == dimenzija && sestavina["tip_id"] == tip){
                return sestavina;
            }
        }
    }

    getPOSTDataForSave(inputs){
        var dict = this.getPOSTData();
        var attributes = {
            "stevilo": $("[attrName='stevilo']",this).get(0).value,
            "sestavina_id": this.getSestavina()["id"],
            "id": this.model["id"],
        }
        if(this.parent.model["tip"] == "vele_prodaja"){
            attributes["cena"] = $("[attrName='cena']",this).get(0).value;
        }
        dict["attributes"] = JSON.stringify(attributes);
        return dict;
    }

    getPOSTDataForCreate(inputs){
        var dict = this.getPOSTData();
        dict["attributes"] = JSON.stringify({
            "stevilo": $("[attrName='stevilo']",this).get(0).value,
            "sestavina_id": this.getSestavina()["id"],
            "baza_id": this.parent.model["id"],
        });
        return dict;
    }
}



window.customElements.define("vnos-model-element",VnosModelElement);