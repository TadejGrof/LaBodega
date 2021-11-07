$(".formset_table .view_button").click(function(){
    var prefix = extractPrefix(this);
    var id = extractId(this);
    var pk = document.getElementById("id_" + prefix + "-" + id + "-id").getAttribute("value");
    window.location.href="ogled/" + pk + "/"; 
})

$("div.formset .edit_all_button").click(function(){
    $(this).closest("div.formset").find("input.toggle_edit").prop('disabled', function(i, v) { return !v; });
});

$("div.formset .edit_selected_button").click(function(){
    $(this).closest("div.formset").find("tr:has(td.index input:checked) input.toggle_edit").prop('disabled', function(i, v) { return !v; });
});

$("div.formset .save_button").click(function(){
    if(Confirm()){
        alert("SAVING");
        form = $(this).attr("form")
        if(!form){
            alert("FORM NOT SET");
        }
    }
})

$("div.formset .delete_all_button").click(function(){
    if(!Confirm()){
        return false;
    }
    alert("WORKING");
    return true;
});

$("div.formset .delete_selected_button").click(function(){
    if(Confirm()){
        alert("DELETING SELECTED");
    }
});
function save_ajax(button){
    var prefix = extractPrefix(button);
    var id = extractId(button);
    var pk = document.getElementById("id_" + prefix + "-" + id + "-id").getAttribute("value");
    $.ajax({
        url: 'save_ajax/' + pk  + "/",
        method: 'POST',
        data: {
            'csrfmiddlewaretoken': "{{csrf_token}}",
        },
        dataType: 'json',
        success: function(data) {
            if(data["success"]){
                populateForm(getForm(prefix,id),data["model"]);
            } else {
                alert(data["error"]);
            }    
        }
    });
}

function delete_ajax(button){
    var prefix = extractPrefix(button);
    var id = extractId(button);
    var pk = document.getElementById("id_" + prefix + "-" + id + "-id").getAttribute("value");
    $.ajax({
        url: 'delete_ajax/' + pk  + "/",
        method: 'POST',
        data: {
            'csrfmiddlewaretoken': "{{csrf_token}}",
        },
        dataType: 'json',
        success: function(data) {
            if(data["success"]){
                deleteForm(prefix,id);
            } else {
                alert(data["error"]);
            }    
        }
    });
}

$(".toggle_edit_button").click(function(){
    var tr = $(this).closest("tr");
    tr.find(".edit_button").toggleClass("inline");
    tr.find("input.toggle_edit").prop('disabled', function(i, v) { return !v; });
});

$(".formset_table .edit_button").click(function(){
    edit_ajax(this);
});

$(".json_button").click(function(){
    var form = this.getAttribute("data-form");
    var pk = $("#id_form-" + form + "-id").val();
    window.location.href="json/" + pk + "/"; 
});

function populateForm(form,data){
    var inputs = $(form).find("input");
    for(var input of inputs){
        var name = input.getAttribute("name");
        if(name in data){
            input.setAttribute("value") = data[name];
        }
    }
}

function getForm(prefix, pk){
    return $("#" + prefix).find("#" + prefix + "-" + formID + "-row")
}

function deleteForm(prefix,pk){
    removeForm(prefix,pk)
    refreshManagementForm(prefix, -1);
    updateForms(prefix);
}

function removeForm(prefix, formID){
    getForm(prefix,formId).remove();
}

function refreshManagementForm(prefix, refresh){
    var totalForms = document.getElementById("id_" + prefix + "-TOTAL_FORMS");
    totalForms.setAttribute('value',parseInt(totalForms.getAttribute('value')) + refresh);
}

function updateForms(prefix) {
    forms = $("#" + prefix).find(".form_row")
    let count = 0;
    for (let form of forms) {
        const formRegex = RegExp(prefix + `-(\\d){1,}-`, 'g');
        form.outerHTML = form.outerHTML.replace(formRegex, prefix + `-${count++}-`)
    }
}

function extractId(element){
    var id = element.getAttribute("id");
    const prefix_regex = new RegExp(".*?-[0-9]{1,}","g");
    var prefix = prefix_regex.exec(id).toString();
    const id_regex = new RegExp("[0-9]{1,}", "g");
    id = id_regex.exec(prefix);
    return id;
}

function extractPrefix(element){
    var id = element.getAttribute("id");
    const regex = new RegExp(".*?-","g");
    var prefix = regex.exec(id);
    if(prefix != null){
        prefix = prefix.toString();
        prefix = prefix.substring(0,prefix.length - 1);
    }
    return prefix;
}