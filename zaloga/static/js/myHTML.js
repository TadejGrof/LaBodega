class MyHTMLElement extends HTMLElement{
    constructor(){
        super();
    }

    connectedCallback(){
        if(this.id == ""){
            this.setId();
        }
    }

    setId(){
        this.id = this.uniqueId();
    }

    uniqueId(){
        return Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
    }

    get filterAttr(){
        return this.getAttribute("filterAttr");
    }

    getFilterValue(){
        return this.getAttribute(this.filterAttr);
    }

    filtriraj(){
        if(this.filterAttr != null){
            var value = this.getFilterValue();
            $("[filter]",this).each(function(){
                $(this).hide();
                if(this.getAttribute("filter") == value){
                    $(this).show();
                }
            });
        }
    }
} 

class IndexElement extends MyHTMLElement{
    constructor(){
        super();
    }

    get scope(){
        if(this.getAttribute("scope") == null){
            return "table";
        }
        return this.getAttribute("scope");
    }

    set scope(data){
        this.setAttribute("scope",data);
    }

    get search(){
        if(this.getAttribute("search") == null){
            return "tr";
        }
        return this.getAttribute("search");
    }

    set search(data){
        return this.setAttribute("search",data)
    }

    refresh(){
        var index = $(this.search,$(this.closest(this.scope)).get(0)).index(this.closest(this.search)) + 1;
        $(this).html(index + ".");
    }
}


window.customElements.define("index-element",IndexElement);