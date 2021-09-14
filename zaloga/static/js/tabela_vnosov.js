
const tabelaVnosovTemplate = document.createElement('template');

tabelaVnosovTemplate.innerHTML = `
    <style>
        div.table{
            width:80%;
            margin:3%;
            margin-left:10%;
        }
        div.tabela_vnosov{
            margin-top:3%;
        }
        div.nov_vnos{
            width:60%;
            margin-left:20%;
            height:30%;
        }
        .datoteka{
            width:150px;
            display:inline-block;
        }
    </style>
    <div class="tabela_vnosov">
        <nov-vnos class="skrit"></nov-vnos>
        <div class="filter">

        </div>
        <div class="table">
            <table class="tabela_vnosov vnosi">

                <tr class="edit">
                    <td width:"10%"> 
                        <button is="toggle-button" toggle="nov-vnos" scope="tabela-vnosov"> Nov vnos </button>
                    </td>
                    <td colspan="2"> 
                        <input class="datoteka" type="file">
                        <button class="inline"> Dodaj iz datoteke </button>
                    </td>
                    <td width="15%"> 
                        <button is="toggle-button" toggle="urediVnos" scope="tabela-vnosov"> Uredi vse </button> 
                    </td>
                    <td width="15%" filter="vele_prodaja"> 
                        <button is="toggle-button" toggle="urediNarocilo" scope="tabela-vnosov"> Uredi </button>
                    </td>
                    <td width="15%" filter="vele_prodaja"> </td>
                    <td width="15%" filter="vele_prodaja"> </td>
                    <td width="15%"> <button class="izbrisi_vse_button"> Izbrisi vse </button> </td>
                </tr>
                <tr class="header">
                    <th> N. </th>
                    <th width="18%"> Dimenzija: </th>
                    <th width="18%"> Tip: </th>
                    <th> Stevilo: </th>
                    <th filter="vele_prodaja"> Narocilo: </th>
                    <th filter="vele_prodaja"> Cena: </th>
                    <th filter="vele_prodaja"> Skupaj: </th>
                    <th width="10%" class="uredi"> Uredi: </th>  
                </tr>
                <tr class="skupno">
                    <td colspan="3"> Skupno število: </td>
                    <td> 
                        <value-element type="int" attrName="skupno_stevilo"> </value-element> 
                    </td>
                    <td filter="vele_prodaja">
                        <value-element type="int" attrName="narocilo"> </value-element> 
                    </td>
                    <td filter="vele_prodaja"> Skupna cena: </td>
                    <td filter="vele_prodaja"> 
                        <value-element type="price" attrName="skupna_cena"> </value-element> 
                    </td>
                    <td> </td>
                </tr>
                <tr filter="vele_prodaja">
                    <td> Popust: </td>
                    <td>
                        <input-value-element type="percent" attrName="popust"> </input-value-element>
                    </td>
                    <td> 
                        <div class="sprememba"> 
                            <button is="toggle-button" scope="tr" toggle=".sprememba"> Sprememba </button>
                        </div>
                        <div class="skrit sprememba"> 
                            <button is="save-button" scope="tr"> OK </button>
                            <button is="toggle-button" scope="tr" toggle=".sprememba"> X </button>
                        </div>
                    </td>
                    <td colspan="3"> Znesek popusta: </td>
                    <td>
                        <value-element type="price" attrName="cena_popusta"> </value-element>
                    </td>
                    <td></td>
                </tr>
                <tr filter="vele_prodaja">
                    <td> Prevoz: </td>
                    <td>
                        <input-value-element type="price" attrName="prevoz"> </input-value-element>
                    </td>
                    <td> 
                        <div class="sprememba"> 
                            <button is="toggle-button" scope="tr" toggle=".sprememba"> Sprememba </button>
                        </div>
                        <div class="skrit sprememba"> 
                            <button is="save-button" scope="tr"> OK </button>
                            <button is="toggle-button" scope="tr" toggle=".sprememba"> X </button>
                        </div>
                    </td>
                    <td colspan="3"> Znesek prevoza: </td>
                    <td>
                        <value-element type="price" attrName="cena_prevoza"> </value-element>
                    </td>
                    <td></td>
                </tr>
                <tr filter="vele_prodaja"">
                    <td colspan="5"> 
                        Koncna cena: 
                    </td>
                    <td> 
                        <value-element type="price" attrName="koncna_cena"> </value-element>
                    </td>
                    <td colspan="2" > </td>
                </tr>
                <tr filter="prevzem">
                    <td colspan="3"> Skupni stroški: </td>
                    <td>  
                        <input-value-element attrName="ladijski_prevoz" type="price"> </input-value-element> 
                    </td>
                    <td >   
                        <div class="sprememba"> 
                            <button is="toggle-button" scope="tr" toggle=".sprememba"> E </button>
                        </div>
                        <div class="skrit sprememba"> 
                            <button is="save-button" scope="tr"> OK </button>
                            <button is="toggle-button" scope="tr" toggle=".sprememba"> X </button>
                        </div>
                    </td>
                    <tr>
                        <td colspan="3"> Razlika: </td>
                        <td>
                             <value-element type="price" attrName="razlika" </value-element>
                        </td>
                        <td>
                        </td>
                    </tr>
                </tr>
            </table>
        </div>
    </div>
    `;

class TabelaVnosov extends ModelsElement {

    constructor(){
        super();
    }

    setAttributes(){
        super.setAttributes();
        this.attrName = "vnosi";
    }

    setContent(){
        this.append(tabelaVnosovTemplate.content.cloneNode(true));
    }   

    connectedCallback(){
        super.connectedCallback();
        var tabela = this;
        $(".izbrisi_vse_button",tabela).click(function(){
            $.ajax({
                url: '/zaloga/ajax/izbrisi_vse/',
                method: 'POST',
                data: {
                'csrfmiddlewaretoken': csrf,
                'baza': tabela.model["id"]
                },
                dataType: 'json',
                success: function (data) {
                    if(data["success"]){
                        $(".vnosRow",tabela).remove();
                        tabela.model = data["baza"];
                    } else {
                        alert("NAPAKA");
                    }
                    
                }
            });
        });
        $('.spremeni_button').click(function(){
            var sprememba = this.getAttribute("data-sprememba");
            $.ajax({
                url: "/zaloga/ajax/spremeni_baza_value/",
                method: 'POST',
                data: {
                'csrfmiddlewaretoken': 'csrf',
                'value': $('.' + sprememba + '_value',tabela).val(),
                'baza': tabela.model["id"],
                'sprememba':sprememba,
                },
                dataType: 'json',
                success: function (data) {
                    if(data["success"]){
                        tabela.model = data["baza"];
                        $("." + sprememba, tabela).toggleClass("skrit");
                    } else {
                        alert("NAPAKA");
                    }
                }
            });  
        });
        this.querySelector('nov-vnos').finalAction = function(){
            var vnos = this.vnos;
            var sestavina = getSestavina(vnos["dimenzija"],vnos["tip"]);
            if(sestavina != null){
                sestavina = sestavina["id"];
                $.ajax({
                    url: '/zaloga/ajax/nov_vnos/',
                    method: 'POST',
                    data: {
                    'csrfmiddlewaretoken': csrf,
                    'sestavina':sestavina,
                    'stevilo':vnos["stevilo"],
                    'baza': tabela.model["id"]
                    },
                    dataType: 'json',
                    success: function (data) {
                        if(data["success"]){
                            tabela.model = data["baza"];
                            tabela.vnosi = data["vnosi"];
                        } else {
                            alert("NAPAKA");
                        } 
                    }
                });
            }   
        }
    }

    removeRows(){
        $("vnos-model-element", this).remove();
    }

    addRows(){
        for(var vnos of this.value){
            var model = document.createElement("vnos-model-element");
            $("table.tabela_vnosov",this).find('tr.skupno').before(model);
            model.model = vnos;
        }
    }

    refresh(){
        this.removeRows();
        this.addRows();
    }
}

window.customElements.define("tabela-vnosov",TabelaVnosov);
