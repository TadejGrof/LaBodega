var valueElementTemplate = document.createElement("template");

valueElementTemplate.innerHTML = `
    <div class="textBox inline">
    </div>
    <div class="valueBox inline">
        <div class="inline value">
        </div>
    </div>
`

class ValueElement extends MyHTMLElement{
    constructor(){
        super();
    }

    get modelElement(){
        return $("#" + this.getAttribute("modelElement")).get(0);
    }

    set modelElement(data){
        this.setAttribute("modelElement",data);
    }

    set type(data){
        this.setAttribute("type",data);
    }

    get type(){
        return this.getAttribute("type");
    }

    get attrName(){
        return this.getAttribute("attrName");
    }

    set attrName(data){
        this.setAttribute("attrName",data);
    }

    set value(data){
        this.setAttribute("value",data);
        $(".value",this).html(data);
    }

    get value(){
        return this.getAttribute("value");
    }

    getAttrName(){
        return this.attrName;
    }

    getAttrNameForDisplay(){
        return this.attrName;
    }

    setAttributes(){
        this.classList.add("valueElement");
        this.classList.add("inline");
        if(this.modelElement == null){this.modelElement = $(this).closest(".modelElement").attr("id");}
        if(this.getAttribute("text") != null){
            $(this).css("text-align","left");
            $(".textBox",this).html(this.getAttribute("text"));
        } else {
            $(".textBox",this).hide();
        }
    }

    setContent(){
        this.append(valueElementTemplate.content.cloneNode(true));
        var valueBox = $(".valueBox",this);
        if(this.type == "price"){
            valueBox.append("<div class='inline'>$</div>");
        } else if(this.type == "percent"){
            valueBox.append("<div class='inline'>%</div>")
        }
    }

    connectedCallback(){
        super.connectedCallback();
        if(this.type == null){this.type="txt"};
        this.setContent();
        this.setAttributes();
    }
}

window.customElements.define("value-element",ValueElement);

class InputValueElement extends ValueElement{
    constructor(){
        super();
    }

    get value(){
        return $("input",this).val();
    }

    set value(data){
        super.value = data;
        $("input",this).val(data);
        $(".inputBox",this).hide();
        $(".valueBox",this).show();
    }

    get connectedFields(){
        var connectedFields = Json.parse(this.getAttrName("connectedFields"))
        if(connectedFields == null){
            return [this];
        } else {
            var fields = [this];
            for(var fieldName of connectedFields){
                fields.push($("[attrName=" + fieldName + "]", this.closest(".modelElement")).get(0));
            }
        }
        return connectedFields;
    }

    setInput(){
        var inputBox = this.querySelector(".inputBox");
        var type = this.type;
        if(this.type == null){this.type="txt"};
        if(this.type == "txt"){
            $(inputBox).append('<input type="text"> </input>');
        } else if( type == "int" || type=="number"){
            $(inputBox).append("<input type='number' step='0.01'> </input>")
        } else if( type == "double"){
            $(inputBox).append(input);
        } else if( type == "price"){
            $(inputBox).append("<input class='inline' type='number' step='0.01'> </input>")
            $(inputBox).append("<div class='inline'>$</div>");
            $("input",inputBox).css("width","80%");
        } else if( type == "percent"){
            $(inputBox).append("<input type='number'> </input>")
            $(inputBox).append("<div class='inline'>%</div>")
            $("input",inputBox).css("width","80%");
        } else if( type == "date"){
            $(inputBox).append("<input type='date'> </input>")
        }
    }

    connectedCallback(){
        super.connectedCallback();
        this.classList.add("inputElement");
        $(this).append("<div class='inputBox inline sprememba'></div>");
        var valueBox = this.querySelector(".valueBox");
        valueBox.classList.add("sprememba");
        if(this.getAttribute("text") != null) $(".inputBox",this).css("width","65%");
        this.setInput();
        $(".inputBox",this).show();
        $(".valueBox",this).hide();
    }
}

window.customElements.define("input-value-element",InputValueElement);

class SelectValueElement extends InputValueElement{
    constructor(){
        super();
    }

    static get observedAttributes(){
        return ["options"];
    }

    get value(){
        return $("select",this).val();
    }

    set value(data){
        super.value = data;
        $("select",this).val(data);
    }

    get options(){
        return JSON.parse(this.getAttribute("options"));
    }

    set options(data){
        this.setAttribute("options",JSON.stringify(data));
        this.setOptions();
    }

    setInput(){
        var select = document.createElement("select");
        var inputBox = this.querySelector(".inputBox");
        $(inputBox).append(select);
    }

    setOptions(){
        for(var option of this.options){
            var element = document.createElement("option");
            element.value = option;
            element.text = option;
            $("select",this).get(0).add(element);
        }
    }

    connectedCallback(){
        this.type = "select";
        this.classList.add("selectElement");
        super.connectedCallback();
        if(this.getAttribute("options") != null){
            var options = this.getAttribute("options")
            this.options = JSON.parse(options.replace(/'/g,'"'))
        };
    }
}

window.customElements.define("select-value-element",SelectValueElement);

class ModelSelectValueElement extends SelectValueElement{
    constructor(){
        super()
    }

    get textAttr(){
        return this.getAttribute("textAttr");
    }

    set textAttr(data){
        this.setAttribute("textAttr",data);
    }

    set value(data){
        super.value = data
        var element = this;
        $("select option",this).each(function(){
            if($(this).html() == data){
                $("select",element).val($(this).val());
                return false;
            }
        });
    }

    get value(){
        return $("select",this).val();
    }

    getAttrNameForDisplay(){
        return this.attrName + "__" + this.textAttr;
    }

    getAttrName(){
        return this.attrName + "_id";
    }

    setOptions(){
        for(var option of this.options){
            var element = document.createElement("option");
            element.value = option["id"];
            element.text = option[this.textAttr];
            $("select",this).get(0).add(element);
        }
    }

    connectedCallback(){
        this.classList.add("modelSelectElement");
        if(this.getAttribute("textAttr") == null){this.textAttr = "id";}
        super.connectedCallback();
    }
}

window.customElements.define("model-select-value-element",ModelSelectValueElement);

class ModelsElement extends ValueElement{
    constructor(){
        super();
    }

    get value(){
        return JSON.parse(this.getAttribute("value"));
    }
    
    set value(data){
        this.setAttribute("value",JSON.stringify(data));
        this.refresh();
    }

    refresh(){

    }

    setContent(){
    
    }

    setAttributes(){
        super.setAttributes();
        this.classList.remove("inline");
        this.classList.add("modelsElement");
        this.type = "models";
    }

    connectedCallback(){
        super.connectedCallback();
        this.classList.add("modelsElement");
    }

}

window.customElements.define("models-element",ModelsElement);


class ModelsTableElement extends ModelsElement{
    constructor(){
        super();
    }

    set rowModel(data){
        this.setAttribute("rowModel",data);
    }

    get rowModel(){
        return $("#" + this.getAttribute("rowModel")).get(0);
    }

    createHeader(){
        var vrstica = document.createElement("tr");
        vrstica.classList.add("header");
        var rowModel = this.rowModel();
        for(var tableCell of $(this).childs()){
            var cell = document.createElement("th");
            $(vrstica).append(cell);
            var valueElement = $(".valueElement",tableCell).get(0);
            if(valueElement != null){
                if(valueElement.text != null){
                    cell.innerHTML = valueElement.text;
                } else {
                    cell.innerHTML = valueElement.attrName.replace("_"," ");
                }
            } else {
                cell.innerHTML = tableCell.getAttribute("text");
            }
        }
        return vrstica;
    }

    setContent(){
        var table = document.createElement("table");
        table.classList.add("tabela_vnosov");
        var rowModel = this.rowModel();
        if(rowModel == null){
            alert("MANJKA ROW MODEL");
        }else{
            var header = this.createHeader();
            $(table).append(header);
        }
    }

    refresh(){
        this.removeRows();
        this.addRows();
    }

    removeRows(){
        $(".rowModelElement",this).remove();
    }

    addRows(){
        var rowModel = this.rowModel;
        for(var model of this.value){
            var row = rowTemplate.content.cloneNode(true);
            $("table.modelTableElement tbody",this).append(row);
            rowModel.model = model;
        }
    }

    connectedCallback(){
        super.connectedCallback();
        this.classList.add("modelsTableElement");
    }
}

window.customElements.define("models-table-element",ModelsTableElement);