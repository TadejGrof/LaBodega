// Inputs that alter all inputs in given scope
// input must aply scope attribute else "body" scope is set
// Also consideres exclude options
$("input:checkbox.selector").change(function() {
    alert("CHANGING");
    var scope = $(this).attr("scope");
    if(!scope) scope = "body";
    var exclude = $(this).attr("exclude");
    var checked = $(this).is(":checked");
    var selector = $(this).attr("selector");
    if(!selector) selector = ""
    $(this).closest(scope).find(selector + " input:checkbox").not(this).not(exclude).prop("checked",checked);    
});


