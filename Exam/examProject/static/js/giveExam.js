// Optimized JavaScript for giveExam.html

var count = 0;
var timerInterval = null;
var dsecElement = null;
var dminElement = null;
var minLabelElement = null;
var secLabelElement = null;

document.addEventListener('DOMContentLoaded', function() {
    // Cache DOM elements for better performance
    dsecElement = document.getElementById("dsec");
    dminElement = document.getElementById("dmin");
    minLabelElement = document.getElementById("min-label");
    secLabelElement = document.getElementById("sec-label");
    
    // Initialize radio button selection handling
    initializeRadioButtons();
    
    // Optimized visibility change detection
    var hidden, visibilityChange, visibilityState;
    if (typeof document.hidden !== "undefined") {
        hidden = "hidden";
        visibilityChange = "visibilitychange";
        visibilityState = "visibilityState";
    } else if (typeof document.msHidden !== "undefined") {
        hidden = "msHidden";
        visibilityChange = "msvisibilitychange";
        visibilityState = "msVisibilityState";
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
    
    // Start timer
    startTimer();
});

// Function to handle radio button selection and visual feedback
function initializeRadioButtons() {
    // Get all radio buttons
    const radioButtons = document.querySelectorAll('input[type="radio"]');
    
    radioButtons.forEach(function(radio) {
        // Add click event listener to the parent label
        const label = radio.closest('label');
        if (label) {
            label.addEventListener('click', function(e) {
                // Prevent default to avoid double-triggering
                e.preventDefault();
                
                // Get the question name to find other options in the same question
                const questionName = radio.name;
                const questionContainer = radio.closest('.question-visible');
                
                // Remove selected state from all options in this question
                const allOptionsInQuestion = questionContainer.querySelectorAll('label');
                allOptionsInQuestion.forEach(function(optionLabel) {
                    optionLabel.classList.remove('bg-blue-100', 'border-blue-500', 'ring-2', 'ring-blue-200');
                    optionLabel.classList.add('border-gray-300');
                });
                
                // Add selected state to clicked option
                label.classList.remove('border-gray-300');
                label.classList.add('bg-blue-100', 'border-blue-500', 'ring-2', 'ring-blue-200');
                
                // Check the radio button
                radio.checked = true;
            });
        }
    });
    
    // Initialize already selected options (for when page loads with saved answers)
    radioButtons.forEach(function(radio) {
        if (radio.checked) {
            const label = radio.closest('label');
            if (label) {
                label.classList.remove('border-gray-300');
                label.classList.add('bg-blue-100', 'border-blue-500', 'ring-2', 'ring-blue-200');
            }
        }
    });
}

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
var seconds = parseInt(document.getElementById("secs")?.value) || 0;
var minutes = parseInt(document.getElementById("mins")?.value) || 0;

function startTimer() {
    // Clear any existing timer
    if (timerInterval) {
        clearInterval(timerInterval);
    }
    
    // Start the countdown
    timerInterval = setInterval(display, 1000);
}

function display() {
    // Check if time is up
    if (minutes <= 0 && seconds <= 0) {
        clearInterval(timerInterval);
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
    
    // Update time
    if (seconds <= 0) {
        minutes = minutes - 1;
        seconds = 59;
    } else {
        seconds = seconds - 1;
    }
    
    // Update DOM elements efficiently
    if (dsecElement) dsecElement.innerHTML = seconds.toString().padStart(2, '0');
    if (dminElement) dminElement.innerHTML = minutes;
    if (minLabelElement) minLabelElement.innerHTML = (minutes == 1) ? "min" : "mins";
    if (secLabelElement) secLabelElement.innerHTML = (seconds == 1) ? "second" : "seconds";
    
    // Add warning colors when time is running low
    if (minutes < 5) {
        if (dminElement) dminElement.style.color = "#dc2626"; // red-600
        if (dsecElement) dsecElement.style.color = "#dc2626"; // red-600
    }
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