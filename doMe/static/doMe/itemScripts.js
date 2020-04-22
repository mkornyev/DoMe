
// Initialize DateTime Picker
$(function () {
    $("#datetimepicker").datetimepicker({
      format: 'DD/MM/YYYY HH:mm',
    });
});

// Prevent empty items
function validateItem(event) {
    var input = $('#newItemInput')[0].value

    if(input.length == 0) {
        $('#newItemInput').focus()
        event.stopPropagation()
        return
    }

    $('#itemPreview').html(input)
}

// Sortable List Scripts

new Sortable(sortablelist, {
    animation: 150,
    ghostClass: 'sortable-ghost'
});

$(".list-group-item").each(function() { 
    this.addEventListener("dragend", function( event ) {
      findMovedItems()
    }, false)
});

function findMovedItems() {
    var index = 0
    var order = null 
    var id = null

    $('.list-group-item').each(function(){
      order = $(this).attr('data-order')
      id = $(this).attr('data-id')

      if(order != index) {
          console.log("Item with id #" + id + "moved from " + order + " to " + index)
          updateBackend(id, index)
      }
      
      index = index + 1
    })
};

function getCSRFToken() {
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
        c = cookies[i].trim();
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length);
        }
    }
    return "unknown";
}

function updateBackend(id, to) {

    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (req.readyState != 4) return;
        if (req.status != 200) return;
        var response = JSON.parse(req.responseText);
        if (response['error'] != null) {
            alert("Error updating list")
        }
    }
    req.open("POST", "/updateItem", true);
    req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    req.send("id=" + id + "&to=" + to + "&csrfmiddlewaretoken=" + getCSRFToken());
}