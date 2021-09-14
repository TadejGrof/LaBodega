
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