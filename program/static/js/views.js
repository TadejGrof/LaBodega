$(".view_button").click(function(){
    var form = this.getAttribute("data-form");
    var pk = $("#id_form-" + form + "-id").val();
    window.location.href="ogled/" + pk + "/"; 
})

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

$(".json_button").click(function(){
    var form = this.getAttribute("data-form");
    var pk = $("#id_form-" + form + "-id").val();
    window.location.href="json/" + pk + "/"; 
});

function deleteForm(prefix,pk){
    removeForm(prefix,pk)
    refreshManagementForm(prefix, -1);
    updateForms(prefix);
}

function removeForm(prefix, formID){
    $("#" + prefix).find("#" + prefix + "-" + formID + "-row").remove();
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