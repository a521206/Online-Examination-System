// Timer and answer preview for giveExam.html

// Update KaTeX preview for a textarea
function updatePreview(textareaId, previewId) {
    const textarea = document.getElementById(textareaId);
    const preview = document.getElementById(previewId);
    if (textarea && preview) {
        preview.innerHTML = textarea.value || 'Your answer will be previewed here...';
        if (window.renderMathInElement) {
            renderMathInElement(preview, {
                delimiters: [
                    {left: "$$", right: "$$", display: true},
                    {left: "$", right: "$", display: false},
                    {left: "\\(", right: "\\)", display: false},
                    {left: "\\[", right: "\\]", display: true}
                ],
                ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"]
            });
        }
    }
}

// Initialize previews for all answer textareas
function initializePreviews() {
    document.querySelectorAll('[id^="answer-"]').forEach(textarea => {
        const qid = textarea.id.replace('answer-', '');
        updatePreview(textarea.id, 'preview-' + qid);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    initializePreviews();
    initializeRadioButtons();
    startTimer();
});

// Simple radio button highlight
function initializeRadioButtons() {
    document.querySelectorAll('input[type="radio"]').forEach(radio => {
        const label = radio.closest('label');
        if (label) {
            label.addEventListener('click', function(e) {
                e.preventDefault();
                const questionContainer = radio.closest('.question-visible');
                questionContainer.querySelectorAll('label').forEach(optionLabel => {
                    optionLabel.classList.remove('bg-blue-100', 'border-blue-500', 'ring-2', 'ring-blue-200');
                    optionLabel.classList.add('border-gray-300');
                });
                label.classList.remove('border-gray-300');
                label.classList.add('bg-blue-100', 'border-blue-500', 'ring-2', 'ring-blue-200');
                radio.checked = true;
            });
        }
        if (radio.checked && label) {
            label.classList.remove('border-gray-300');
            label.classList.add('bg-blue-100', 'border-blue-500', 'ring-2', 'ring-blue-200');
        }
    });
}

// Timer logic
var seconds = parseInt(document.getElementById("secs")?.value) || 0;
var minutes = parseInt(document.getElementById("mins")?.value) || 0;
var timerInterval = null;

function startTimer() {
    if (timerInterval) clearInterval(timerInterval);
    timerInterval = setInterval(display, 1000);
}

function display() {
    if (minutes <= 0 && seconds <= 0) {
        clearInterval(timerInterval);
        document.getElementById("examform").submit();
        return;
    }
    if (seconds <= 0) {
        minutes -= 1;
        seconds = 59;
    } else {
        seconds -= 1;
    }
    document.getElementById("dsec").innerHTML = seconds.toString().padStart(2, '0');
    document.getElementById("dmin").innerHTML = minutes;
    document.getElementById("min-label").innerHTML = (minutes == 1) ? "min" : "mins";
    document.getElementById("sec-label").innerHTML = (seconds == 1) ? "second" : "seconds";
    if (minutes < 5) {
        document.getElementById("dmin").style.color = "#dc2626";
        document.getElementById("dsec").style.color = "#dc2626";
    }
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