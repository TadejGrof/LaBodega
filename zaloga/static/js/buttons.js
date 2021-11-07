
class ToggleButton extends HTMLButtonElement {
    constructor() {
        super();
        this.addEventListener('click', function(){
            $(this.toggle,this.closest(this.scope)).toggle();
        });
    }

    set scope(data){
        this.setAttribute("scope",data);
    }

    get scope(){
        var value = this.getAttribute("scope");
        if(value == null){
            return "body";
        }
        return this.getAttribute("scope");
    }

    set toggleClass(data){
        this.setAttribute("toggleClass",data);
    }

    get toggleClass(){
        var value = this.getAttribute("toggleClass");
        if(value == null){
            return "skrit";
        }
        return this.getAttribute("toggleClass");
    }

    set toggle(data){
        this.setAttribute("toggle",data);
    }

    get toggle(){
        if(this.getAttribute("toggle") == null){
            return ".edit, .sprememba";
        }
        return this.getAttribute("toggle");
    }

    connectedCallback(){
    }
}

window.customElements.define("toggle-button",ToggleButton,{extends:"button"});


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
