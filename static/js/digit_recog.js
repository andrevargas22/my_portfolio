console.log("API Endpoint:", window.apiEndpoint);

// Set up the canvas
var canvas = document.getElementById("canvas");
var ctx = canvas.getContext("2d");
ctx.lineWidth = 20;
ctx.lineJoin = 'round';
ctx.lineCap = 'round';

// Set up mouse events for drawing
var drawing = false;
var mousePos = { x: 0, y: 0 };
var lastPos = mousePos;

canvas.addEventListener("mousedown", function (e) {
    drawing = true;
    lastPos = getMousePos(canvas, e);
}, false);

canvas.addEventListener("mouseup", function (e) {
    drawing = false;
}, false);

canvas.addEventListener("mousemove", function (e) {
    mousePos = getMousePos(canvas, e);
}, false);

// Get the position of the mouse relative to the canvas
function getMousePos(canvasDom, mouseEvent) {
    var rect = canvasDom.getBoundingClientRect();
    return {
        x: mouseEvent.clientX - rect.left,
        y: mouseEvent.clientY - rect.top
    };
}

// Get a regular interval for drawing to the screen
window.requestAnimFrame = (function (callback) {
    return window.requestAnimationFrame ||
        window.webkitRequestAnimationFrame ||
        window.mozRequestAnimationFrame ||
        window.oRequestAnimationFrame ||
        window.msRequestAnimaitonFrame ||
        function (callback) {
            window.setTimeout(callback, 1000 / 60);
        };
})();

// Draw to the canvas
function renderCanvas() {
    if (drawing) {
        ctx.moveTo(lastPos.x, lastPos.y);
        ctx.lineTo(mousePos.x, mousePos.y);
        ctx.stroke();
        lastPos = mousePos;
    }
}

// Allow for animation
(function drawLoop() {
    requestAnimFrame(drawLoop);
    renderCanvas();
})();

// Set up touch events for mobile, etc
canvas.addEventListener("touchstart", function (e) {
    mousePos = getTouchPos(canvas, e);
    var touch = e.touches[0];
    var mouseEvent = new MouseEvent("mousedown", {
        clientX: touch.clientX,
        clientY: touch.clientY
    });
    canvas.dispatchEvent(mouseEvent);
}, false);

canvas.addEventListener("touchend", function (e) {
    var mouseEvent = new MouseEvent("mouseup", {});
    canvas.dispatchEvent(mouseEvent);
}, false);

canvas.addEventListener("touchmove", function (e) {
    var touch = e.touches[0];
    var mouseEvent = new MouseEvent("mousemove", {
        clientX: touch.clientX,
        clientY: touch.clientY
    });
    canvas.dispatchEvent(mouseEvent);
}, false);

// Get the position of a touch relative to the canvas
function getTouchPos(canvasDom, touchEvent) {
    var rect = canvasDom.getBoundingClientRect();
    return {
        x: touchEvent.touches[0].clientX - rect.left,
        y: touchEvent.touches[0].clientY - rect.top
    };
}

// Prevent scrolling when touching the canvas
document.body.addEventListener("touchstart", function (e) {
    if (e.target == canvas) {
        e.preventDefault();
    }
}, false);

document.body.addEventListener("touchend", function (e) {
    if (e.target == canvas) {
        e.preventDefault();
    }
}, false);

document.body.addEventListener("touchmove", function (e) {
    if (e.target == canvas) {
        e.preventDefault();
    }
}, false);

// Clear the canvas
function clean() {
    canvas.width = canvas.width;
    ctx.lineWidth = 20;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';

    // Limpar o div de resultados ao limpar o canvas
    var resultDiv = document.getElementById("result");
    resultDiv.innerHTML = "";
}

function animateProgressBar(element, targetPercentage, progressBarColor) {
    element.classList.add(progressBarColor);
    let width = 0;
    const interval = setInterval(function() {
        if (width >= targetPercentage) {
            clearInterval(interval);
        } else {
            width++;
            element.style.width = width + '%';
            element.setAttribute('aria-valuenow', width);
            element.innerHTML = width + '%';
        }
    }, 10);
}


// On call, send data to server
function predict() {
    var resultDiv = document.getElementById("result");
    
    // Limpar o div de resultados e mostrar o texto "Loading..."
    resultDiv.innerHTML = "Loading...";
    
    // Convert canvas to DataURL
    var dataURL = canvas.toDataURL();
    
    // Ajax post to route /predict
    $.ajax({
        type: "POST",
        url: apiEndpoint,  // Updated URL for FastAPI
        contentType: "application/json",
        data: JSON.stringify({
            imageBase64: dataURL
        }),
        
        // If success:
        success: function(response) {
            // Handle the response
            var predictions = response.predictions;
            resultDiv.innerHTML = "<h3>Top 3 Predictions:</h3>";

            for (var i = 0; i < predictions.length; i++) {
                var digit = predictions[i].digit;
                var probability = (predictions[i].probability * 100).toFixed(2);
                var progressBarColor = i === 0 ? "bg-success" : i === 1 ? "bg-primary" : "bg-danger";
                
                resultDiv.innerHTML += `
                    <div class="d-flex align-items-center my-1">
                        <strong>${digit}:</strong>
                        <div class="progress flex-grow-1 mx-2" style="height: 20px;">
                            <div class="progress-bar ${progressBarColor}" role="progressbar" style="width: 0%;" aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
                        </div>
                    </div>
                `;
            }

            // Animate progress bars
            var progressBars = resultDiv.querySelectorAll('.progress-bar');
            for (var i = 0; i < progressBars.length; i++) {
                var targetPercentage = predictions[i].probability * 100;
                var progressBarColor = i === 0 ? "bg-success" : i === 1 ? "bg-primary" : "bg-danger";
                animateProgressBar(progressBars[i], targetPercentage, progressBarColor);
            }
        },
        // If error:
        error: function() {
            resultDiv.innerHTML = "An error occurred while processing the request.";
        }
    });
}
