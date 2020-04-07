
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