// CircuitAI - Main Client Script for Engineering CAD Simulator

document.addEventListener("DOMContentLoaded", function () {
    // Sidebar toggle for smaller screens
    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebar = document.querySelector(".sidebar");

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener("click", function () {
            sidebar.classList.toggle("show");
        });
    }

    // Prediction Form Submission Spinner
    const circuitForm = document.getElementById("circuitForm");
    const loadingSpinner = document.getElementById("loadingSpinner");

    if (circuitForm) {
        circuitForm.addEventListener("submit", function (e) {
            if (circuitForm.checkValidity()) {
                if (loadingSpinner) {
                    loadingSpinner.style.display = "flex";
                }
            }
        });
    }

    // Initialize Gauge Meter if canvas element exists
    const gaugeCanvas = document.getElementById("gaugeCanvas");
    if (gaugeCanvas) {
        const score = parseFloat(gaugeCanvas.getAttribute("data-score") || "95.0");
        drawGaugeMeter(gaugeCanvas, score);
    }
});

// Function to draw CAD Gauge Meter on Canvas
function drawGaugeMeter(canvas, score) {
    const ctx = canvas.getContext("2d");
    const cx = canvas.width / 2;
    const cy = canvas.height - 10;
    const radius = 65;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Background Arc
    ctx.beginPath();
    ctx.arc(cx, cy, radius, Math.PI, 2 * Math.PI, false);
    ctx.lineWidth = 12;
    ctx.strokeStyle = "rgba(255, 255, 255, 0.1)";
    ctx.stroke();

    // Value Arc
    const pct = Math.min(Math.max(score, 0), 100) / 100;
    const endAngle = Math.PI + pct * Math.PI;

    ctx.beginPath();
    ctx.arc(cx, cy, radius, Math.PI, endAngle, false);
    ctx.lineWidth = 12;
    
    // Gradient
    const grad = ctx.createLinearGradient(0, 0, canvas.width, 0);
    grad.addColorStop(0, "#2563eb");
    grad.addColorStop(1, "#06b6d4");
    ctx.strokeStyle = grad;
    ctx.stroke();

    // Score Text
    ctx.font = "bold 20px Outfit, sans-serif";
    ctx.fillStyle = "#ffffff";
    ctx.textAlign = "center";
    ctx.fillText(score.toFixed(1) + "%", cx, cy - 20);

    ctx.font = "10px Plus Jakarta Sans, sans-serif";
    ctx.fillStyle = "#94a3b8";
    ctx.fillText("SCORE", cx, cy - 5);
}

// Function to download PDF simulation report
function downloadPDFReport(title) {
    window.print();
}
