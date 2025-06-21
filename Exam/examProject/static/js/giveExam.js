// JavaScript moved from giveExam.html

var count = 0;
document.addEventListener('DOMContentLoaded', function() {
    var hidden, visibilityState, visibilityChange;
    if (typeof document.hidden !== "undefined") {
        hidden = "hidden", visibilityChange = "visibilitychange", visibilityState = "visibilityState";
    } else if (typeof document.msHidden !== "undefined") {
        hidden = "msHidden", visibilityChange = "msvisibilitychange", visibilityState = "msVisibilityState";
    }
    var document_hidden = document[hidden];
    document.addEventListener(visibilityChange, function() {
        if(document_hidden != document[hidden]) {
            if(document[hidden]) {
                count+=1;
                if(count == 5){
                    console.log("DONE")
                    mail()
                }
            }
            document_hidden = document[hidden];
        }
    });
});

function mail(){
    var professorname = document.getElementById("professorname").value;
    fetch(`/student/cheat/${professorname}`,{
        method:"GET",
        credentials: "same-origin",
        headers: {
            "X-CSRFToken": getCookie("csrftoken"),
            "Accept": "application/json",
            "Content-Type": "application/json"
        },
    })
}

var milisec = 0;
var seconds = document.getElementById("secs").value;
var minutes = document.getElementById("mins").value
function display() {
    if (minutes == 0 && seconds == 0) {
        document.getElementById("examform").submit();
    }
    if (seconds == 0) {
        minutes = minutes - 1
        seconds = 60
    }
    seconds -= 1
    document.getElementById("dsec").innerHTML = seconds
    document.getElementById("dmin").innerHTML = minutes
    document.getElementById("min-label").innerHTML = (minutes == 1) ? "min" : "mins";
    document.getElementById("sec-label").innerHTML = (seconds == 1) ? "second" : "seconds";
    setTimeout(display, 1000)
}
display()

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
} 