
class ModelElement extends MyHTMLElement{
    constructor(){
        super();
    }

    get model(){
        return JSON.parse(this.getAttribute("model"));
    }
    
    set model(data){
        this.setAttribute("model",JSON.stringify(data));
        this.modelChange(data);
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


    refresh(model){
        if(model == null) model = this.model;
        var filterAttr = this.filterAttr;
        if(filterAttr != null){
            $("[filter]",this).each(function(){
                $(this).hide()
                if(this.getAttribute("filter") == model[filterAttr]){
                    $(this).show();
                }
            });
        };
    }


    getPOSTData(){
        return {
            'csrfmiddlewaretoken': csrf,
            'class_name': this.className,
            'hasParent': this.hasParent,
            "parentAttr": this.parentAttr,
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

    save(scopeElement=null, includeParent=true){
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
                    element.postSave(data, includeParent);
                } else {
                    alert(data["error"]);
                }    
            }
        });
    }

    postSave(data, includeParent){
        this.model = data["model"];
        if(this.hasParent && includeParent){
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
        $(this).remove();
        if(this.hasParent && includeParent){
            this.parent.model = data["parent"];
        }
    };
}

window.customElements.define("model-element",ModelElement);

class EditModelButton extends HTMLButtonElement{
    set modelElement(data){
        this.setAttribute("modelElement",data)
    }

    get modelElement(){
        return $("#" + this.getAttribute("modelElement")).get(0);
    }

    get validate(){
        var validate = this.getAttribute("validate");
        if(validate == "true"){ return true;}
        return false;
    }

    set validate(data){
        this.setAttribute("validate",data.toString())
    }

    set scope(data){
        this.setAttribute("scope",data);
    }

    get scope(){
        return this.getAttribute("scope");
    }

    setClickEvent(){

    }

    connectedCallback(){
        this.classList.add("editButton");
        if(this.scope == null){this.scope = ".modelElement";}
        var modelElement = this.getAttribute("modelElement");
        if(modelElement == null){
            this.modelElement = $(this).closest(".modelElement").attr("id");
        }
        this.setClickEvent();
    }
}

class SaveModelButton extends EditModelButton{
    constructor(){
        super();
    }

    setClickEvent(){
        var validate = this.validate;
        $(this).click(function(){
            if(this.validate && !Confirm()){return}
            this.modelElement.save($(this).closest(this.scope).get(0));
            $(".sprememba, .edit",$(this).closest(this.scope).get(0)).toggle();
        })
    }

    connectedCallback(){
        super.connectedCallback();
        this.classList.add("saveButton");
    }
    
}

window.customElements.define("save-button",SaveModelButton,{extends:"button"});

class CreateModelButton extends EditModelButton{
    constructor(){
        super();
    }

    setClickEvent(){
        var validate = this.validate;
        $(this).click(function(){
            if(this.validate && !Confirm()){return}
            this.modelElement.create($(this).closest(this.scope).get(0));
        })
    }

    connectedCallback(){
        super.connectedCallback();
        this.classList.add("createButton");
    }
    
}

window.customElements.define("create-button",CreateModelButton,{extends:"button"});

class DeleteModelButton extends EditModelButton{
    constructor(){
        super();
    }

    setClickEvent(){
        var validate = this.validate;
        $(this).click(function(){
            if(validate && !Confirm()){return}
            this.modelElement.delete();
        })
    }

    connectedCallback(){
        super.connectedCallback();
        this.classList.add("deleteButton");
    }
    
}

window.customElements.define("delete-button",DeleteModelButton,{extends:"button"});


class RowModelElement extends ModelElement{
    constructor(){
        super();
    }

    connectedCallback(){
        super.connectedCallback();
        this.classList.add("rowModelElement");
        $(this).css("display","table-row");
    }
}

window.customElements.define("row-model-element",RowModelElement);