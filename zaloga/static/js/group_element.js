class ClassModelElement extends MyHTMLElement{

}

class ModelsTableElement extends ModelsElement{
    constructor(){
        super();
    }

    get rowModel(){
        return this.getAttribute("rowModel");
    }

    connectedCallback(){
        var table = document.createElement("table");
        var tbody = document.createElement("tbody");
        $(this).append(table);
        $(table).append(tbody);
        table.classList.add("tabela_vnosov");
        table.classList.add("modelTableElement");
        if(this.getAttribute("header") != null){
            var header = $("#" + this.getAttribute("header")).get(0).content.cloneNode(true);
            $("tbody",table).append(header);
        } 
        if(this.getAttribute("value") != null){
            this.value = this.getAttribute("value");
        } 
    }

    refresh(){
        this.removeRows();
        this.addRows();
        this.filtriraj();
    }

    removeRows(){
        $(".vnosModel",this).remove();
    }

    addRows(){
        var rowTemplate = $("#" + this.rowModel).get(0)
        for(var model of this.value){
            var row = rowTemplate.content.cloneNode(true);
            $("table.modelTableElement tbody",this).append(row);
            var rowModel = $("table.modelTableElement tbody .rowModelElement").last().get(0);
            rowModel.model = model;
        }
    }
}

window.customElements.define("models-table-element",ModelsTableElement);