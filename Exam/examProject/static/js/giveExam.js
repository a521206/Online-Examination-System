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
var seconds = parseInt(document.getElementById("secs").value) || 0;
var minutes = parseInt(document.getElementById("mins").value) || 0;

function display() {
    // Check if time is up
    if (minutes <= 0 && seconds <= 0) {
        // Show warning and auto-submit
        if (confirm("Time's up! Your exam will be submitted automatically.")) {
            document.getElementById("examform").submit();
        } else {
            document.getElementById("examform").submit();
        }
        return;
    }
    
    // Show warning when 5 minutes remaining
    if (minutes === 5 && seconds === 0) {
        alert("Warning: Only 5 minutes remaining!");
    }
    
    // Show warning when 1 minute remaining
    if (minutes === 1 && seconds === 0) {
        alert("Warning: Only 1 minute remaining!");
    }
    
    // Update display
    if (seconds <= 0) {
        minutes = minutes - 1;
        seconds = 59;
    } else {
        seconds = seconds - 1;
    }
    
    // Update DOM elements
    var dsecElement = document.getElementById("dsec");
    var dminElement = document.getElementById("dmin");
    var minLabelElement = document.getElementById("min-label");
    var secLabelElement = document.getElementById("sec-label");
    
    if (dsecElement) dsecElement.innerHTML = seconds.toString().padStart(2, '0');
    if (dminElement) dminElement.innerHTML = minutes;
    if (minLabelElement) minLabelElement.innerHTML = (minutes == 1) ? "min" : "mins";
    if (secLabelElement) secLabelElement.innerHTML = (seconds == 1) ? "second" : "seconds";
    
    // Add warning colors when time is running low
    if (minutes < 5) {
        if (dminElement) dminElement.style.color = "#dc2626"; // red-600
        if (dsecElement) dsecElement.style.color = "#dc2626"; // red-600
    }
    
    // Continue countdown
    setTimeout(display, 1000);
}

// Start the timer when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', display);
} else {
    display();
}

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