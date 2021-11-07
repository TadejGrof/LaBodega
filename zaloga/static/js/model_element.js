
class ModelElement extends MyHTMLElement{
    constructor(){
        super();
    }

    get model(){
        return JSON.parse(this.getAttribute("model"));
    }
    
    set model(data){
        this.setModel(data);
    }

    setModel(data,change=true){
        this.setAttribute("model",JSON.stringify(data));
        if(change) this.modelChange(data);
    }

    updateField(fieldName, value){}

    get filterAttr(){
        return this.getAttribute("filterAttr");
    }

    set filterAttr(data){
        this.setAttribute("filterAttr",data)
    }

    get parent(){
        return $("#" + this.getAttribute("parent")).get(0);
    }

    set parent(data){
        this.setAttribute("parent",data);
    }

    get hasParent(){
        return this.parent != null;
    }

    get parentAttr(){
        return this.getAttribute("parentAttr");
    }

    set parentAttr(data){
        this.setAttribute("parentAttr",data);
    }

    static get observedAttributes(){    
        return ["model"];
    }

    get className(){
        return this.getAttribute("className");
    }

    set className(data){
        this.setAttribute("className",data);
    }

    valueElements(scopeElement = this){
        return $('.valueElement',scopeElement).filter("[modelElement=" + this.id + "]") 
    }

    inputElements(scopeElement = this){
        var inputs = $('.inputElement',scopeElement).filter("[modelElement=" + this.id + "]");
        return inputs;
    }

    modelChange(model){
        this.valueElements().each(function(){
            var attrName = this.getAttrNameForDisplay();
            if(attrName in model){
                this.value = model[attrName];
            }     
        });
        this.refresh(model);
    }

    connectedCallback(){
        super.connectedCallback();
        this.classList.add("modelElement");
        if(this.getAttribute("parent") == null){
            var parent = $(this).parent().closest(".modelElement");
            if(parent.length > 0){
                this.parent = parent.get(0).id;
            };
        }
    }

    getPOSTData(){
        return {
            'csrfmiddlewaretoken': csrf,
            'class_name': this.className,
            'hasParent': this.hasParent,
        };
    }

    getPOSTDataForSave(inputs){
        var dict = this.getPOSTData();
        dict["attributes"] = this.getPOSTAttributesData(inputs);
        return dict;
    }

    getPOSTAttributesData(inputs){
        var model = this.model;
        var attributes = {};
        if(model != null){
            attributes["id"] = model["id"];
        }
        for(var input of inputs){
            attributes[input.getAttrName()] = input.value;
        }
        return JSON.stringify(attributes);
    }
    
    preSave(){};

    save(scopeElement=null){
        if(scopeElement == null){
            scopeElement = this;
        }
        var element = this;
        element.preSave();
        $.ajax({
            url: '/zaloga/ajax/save/',
            method: 'POST',
            data: element.getPOSTDataForSave(element.inputElements(scopeElement)),
            dataType: 'json',
            success: function (data) {
                if(data["success"]){
                    element.postSave(data);
                } else {
                    alert(data["error"]);
                }    
            }
        });
    }

    connectedFields(inputElements){
        var fields = []
        for(var input of inputElements){
            for(var field of input.connectedFields){
                if(!fields.contains(field)){
                    fields.push(field);
                }
            }
        }
        return fields;
    }

    postSave(data){
        var data = data["model"];
        for(var field of this.connectedFields(updatedFields)){
            this.updateField(field,data[field.attrName]);
        }
        if(this.hasParent){
            element.parent.model = data["parent"];
        }
    };


    getPOSTDataForCreate(inputs){
        return this.getPOSTDataForSave(inputs);
    }

    preCreate(){};

    create(scopeElement=null, includeParent=true){
        if(scopeElement == null){
            scopeElement = this;
        }
        var element = this;
        element.preCreate();
        $.ajax({
            url: '/zaloga/ajax/create/',
            method: 'POST',
            data: element.getPOSTDataForCreate(element.inputElements(scopeElement)),
            dataType: 'json',
            success: function (data) {
                if(data["success"]){
                    element.postCreate(data, includeParent);
                } else {
                    alert(data["error"]);
                }    
            }
        });
    }

    postCreate(data, includeParent){
        if(this.hasParent && includeParent){
            this.parent.model = data["parent"];
        }
    };

    getPOSTDataForDelete(){
        var dict = this.getPOSTData();
        dict["attributes"] = JSON.stringify(
            {
                "id": this.model["id"]
            }
        )
        return dict;
    }

    preDelete(){};

    delete(scopeElement=null, includeParent=true){
        if(scopeElement == null){
            scopeElement = this;
        }
        var element = this;
        element.preDelete();
        $.ajax({
            url: '/zaloga/ajax/delete/',
            method: 'POST',
            data: element.getPOSTDataForDelete(),
            dataType: 'json',
            success: function (data) {
                if(data["success"]){
                    element.postDelete(data, includeParent);
                } else {
                    alert(data["error"]);
                }    
            }
        });
    }

    postDelete(data, includeParent){
        this.model = null;
        if(this.hasParent && includeParent){
            this.parent.model = data["parent"];
        }
    };
}

window.customElements.define("model-element",ModelElement);

class RowModelElement extends ModelElement{
    constructor(){
        super();
    }

    get table(){
        return $("#" + this.getAttribute("table")).get(0);
    }

    set table(data){
        this.setAttribute("table",data);
    }

    connectedCallback(){
        super.connectedCallback();
        this.classList.add("rowModelElement");
        this.table = $(this).closest(".modelTableElement").get(0).id;
    }

    refreshParent(data){
        var parent = data["parent"];
        var table = this.table;
        for(var field of table.connectedFields()){
            field.updateField(field,parent[field.attrName]);
        }
        this.parent.setModel(parent);
    }

    postSave(data){
        this.model = data["model"];
        this.refreshParent(data);
    }

    postDelete(data){
        $(this).remove();
        this.refreshParent(data);
    }

    postCreate(data){
        this.model = data["model"];
        this.refreshParent(data);
    }
}

window.customElements.define("row-model-element",RowModelElement);
