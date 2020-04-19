

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

function searchMembers(val) {
    console.log('Searching')
    console.log(val)

    var bar = $('#searchBar')[0]

    if(bar.html() === "") { return }

    var content = bar.html()

    var req = new XMLHttpRequest();
    req.onreadystatechange = function() {
        if (req.readyState != 4) return;
        if (req.status != 200) return;
        var response = JSON.parse(req.responseText);
        if (response['error'] != null) {
            displayError(response.error);
            alert("Error")
        }
    }
    req.open("POST", "/searchMembers", true);
    req.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    req.send("query=" + content + "&csrfmiddlewaretoken="+getCSRFToken());
}