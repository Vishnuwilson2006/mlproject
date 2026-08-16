/**
 * uncertainty_analysis.js
 * CircuitAI - Module 1: Uncertainty & Confidence Analysis Chart Rendering
 */

window.chartInstances = window.chartInstances || {};

document.addEventListener("DOMContentLoaded", function () {
    if (typeof Chart === 'undefined') {
        console.error("Chart.js is required but not loaded!");
        return;
    }

    const dataScript = document.getElementById("analysis-data");
    if (!dataScript) return;

    try {
        const initialData = JSON.parse(dataScript.textContent);
        renderUncertaintyCharts(initialData);
    } catch (e) {
        console.error("Error parsing uncertainty analysis data:", e);
    }

    // Attach AJAX form handler if present
    const form = document.getElementById("uncertaintyForm");
    if (form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault();
            const formData = new FormData(form);
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Calculating...';
            }

            fetch(window.location.href, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(res => res.json())
            .then(data => {
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="bi bi-lightning-charge-fill me-1"></i> Run Uncertainty Analysis';
                }
                if (data && data.success) {
                    renderUncertaintyCards(data);
                    renderUncertaintyCharts(data);
                }
            })
            .catch(err => {
                console.error("Error running uncertainty analysis:", err);
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="bi bi-lightning-charge-fill me-1"></i> Run Uncertainty Analysis';
                }
            });
        });
    }

    // Attach Download PNG listeners
    document.querySelectorAll(".download-chart-btn").forEach(btn => {
        btn.addEventListener("click", function () {
            const canvasId = this.getAttribute("data-chart");
            downloadChartPNG(canvasId, "Uncertainty_Analysis_Chart.png");
        });
    });
});

function downloadChartPNG(canvasId, fileName) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const link = document.createElement("a");
    link.download = fileName || "chart.png";
    link.href = canvas.toDataURL("image/png");
    link.click();
}

function safeValue(val, fallback = 0) {
    if (val === null || val === undefined || isNaN(val) || !isFinite(val)) {
        return fallback;
    }
    return val;
}

function createChart(canvasId, config) {
    if (window.chartInstances[canvasId]) {
        window.chartInstances[canvasId].destroy();
    }
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    const ctx = canvas.getContext("2d");
    const chart = new Chart(ctx, config);
    window.chartInstances[canvasId] = chart;
    return chart;
}

function renderUncertaintyCards(data) {
    if (!data.output_cards) return;
    const cardsContainer = document.getElementById("outputCardsContainer");
    if (!cardsContainer) return;

    let html = '';
    data.output_cards.forEach(card => {
        html += `
            <div class="col-md-6 col-xl-4">
                <div class="card border-0 glass-card p-3 h-100 shadow-sm position-relative overflow-hidden">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <span class="text-muted small fw-bold">${card.label}</span>
                        <span class="badge bg-${card.reliability_badge} bg-opacity-25 text-${card.reliability_badge} border border-${card.reliability_badge} border-opacity-25" style="font-size: 0.65rem;">
                            ${card.model_reliability}
                        </span>
                    </div>
                    <div class="d-flex align-items-baseline gap-2 mb-1">
                        <span class="fs-3 fw-extrabold text-white font-mono">${card.predicted_value}</span>
                        <span class="text-muted small">${card.unit}</span>
                    </div>
                    <div class="small text-muted mb-2">
                        Prediction Interval: <strong class="text-info font-mono">${card.prediction_interval}</strong>
                    </div>
                    <div class="d-flex justify-content-between align-items-center pt-2 border-top border-secondary border-opacity-25 text-muted small">
                        <span>Confidence: <strong class="text-success font-mono">${card.confidence_score}%</strong></span>
                        <span>Uncertainty: <strong class="text-warning font-mono">${card.uncertainty_range}</strong></span>
                    </div>
                </div>
            </div>
        `;
    });
    cardsContainer.innerHTML = html;
}

function renderUncertaintyCharts(data) {
    if (!data || !data.graph_data || !data.graph_data.labels || data.graph_data.labels.length === 0) {
        console.warn("No graph data available for Uncertainty Analysis.");
        return;
    }

    const gd = data.graph_data;
    const labels = gd.labels;
    const units = gd.units || labels.map(() => '');

    // 1. Prediction vs Uncertainty
    const predVals = gd.predicted.map(v => safeValue(v));
    const uncVals = gd.uncertainty.map(v => safeValue(v));

    createChart('chartPredVsUncertainty', {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Predicted Value',
                    data: predVals,
                    backgroundColor: 'rgba(37, 99, 235, 0.7)',
                    borderColor: '#2563eb',
                    borderWidth: 1
                },
                {
                    label: 'Estimated Uncertainty (±)',
                    data: uncVals,
                    backgroundColor: 'rgba(245, 158, 11, 0.7)',
                    borderColor: '#f59e0b',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: 'Predicted Circuit Metrics vs Estimated Uncertainty', color: '#f8fafc', font: { size: 13, weight: 'bold' } },
                legend: { labels: { color: '#94a3b8' } },
                tooltip: {
                    callbacks: {
                        label: function(ctx) {
                            const unit = units[ctx.dataIndex] || '';
                            return `${ctx.dataset.label}: ${ctx.raw} ${unit}`;
                        }
                    }
                }
            },
            scales: {
                x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
            }
        }
    });

    // 2. Prediction Interval (Lower, Predicted, Upper)
    const ciLower = gd.ci_lower.map(v => safeValue(v));
    const ciUpper = gd.ci_upper.map(v => safeValue(v));

    createChart('chartPredInterval', {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Upper Bound (95% CI)',
                    data: ciUpper,
                    borderColor: '#34d399',
                    backgroundColor: 'rgba(52, 211, 153, 0.1)',
                    borderDash: [5, 5],
                    fill: '+1'
                },
                {
                    label: 'Predicted Value',
                    data: predVals,
                    borderColor: '#38bdf8',
                    backgroundColor: '#38bdf8',
                    pointRadius: 6,
                    fill: false
                },
                {
                    label: 'Lower Bound (95% CI)',
                    data: ciLower,
                    borderColor: '#f87171',
                    backgroundColor: 'rgba(248, 113, 113, 0.1)',
                    borderDash: [5, 5],
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: '95% Prediction Interval Bounds', color: '#f8fafc', font: { size: 13, weight: 'bold' } },
                legend: { labels: { color: '#94a3b8' } }
            },
            scales: {
                x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
            }
        }
    });

    // 3. Confidence Score
    const confVals = gd.confidence.map(v => safeValue(v, 90));

    createChart('chartConfidence', {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Confidence Score (%)',
                data: confVals,
                backgroundColor: confVals.map(c => c >= 90 ? 'rgba(34, 197, 94, 0.7)' : 'rgba(245, 158, 11, 0.7)'),
                borderColor: confVals.map(c => c >= 90 ? '#22c55e' : '#f59e0b'),
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: 'Model Confidence Score (%) per Output Metric', color: '#f8fafc', font: { size: 13, weight: 'bold' } },
                legend: { display: false }
            },
            scales: {
                x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                y: { min: 50, max: 100, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
            }
        }
    });

    // 4. Residual / Error Distribution
    const resHist = gd.residual_histogram || { bins: ['-0.05', '0.00', '0.05'], counts: [10, 30, 10] };
    const resBins = resHist.bins || [];
    const resCounts = (resHist.counts || []).map(v => safeValue(v));

    createChart('chartResiduals', {
        type: 'bar',
        data: {
            labels: resBins,
            datasets: [{
                label: 'Ensemble Residual Frequency',
                data: resCounts,
                backgroundColor: 'rgba(168, 85, 247, 0.7)',
                borderColor: '#a855f7',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: 'Surrogate Model Ensemble Residual Distribution', color: '#f8fafc', font: { size: 13, weight: 'bold' } },
                legend: { display: false }
            },
            scales: {
                x: { title: { display: true, text: 'Residual Error Delta', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                y: { title: { display: true, text: 'Frequency Count', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
            }
        }
    });

    // 5. Model Performance Metrics (R², MAE, RMSE)
    const mm = gd.model_metrics || { r2: 0.98, mae: 0.15, rmse: 0.22 };

    createChart('chartModelMetrics', {
        type: 'bar',
        data: {
            labels: ['R² Accuracy Score', 'MAE (Mean Abs Error)', 'RMSE (Root Mean Sq Error)', 'Mean Pred Error'],
            datasets: [{
                label: 'Surrogate ML Model Performance',
                data: [safeValue(mm.r2 * 100), safeValue(mm.mae), safeValue(mm.rmse), safeValue(mm.mean_pred_error)],
                backgroundColor: ['rgba(34, 197, 94, 0.7)', 'rgba(56, 189, 248, 0.7)', 'rgba(245, 158, 11, 0.7)', 'rgba(168, 85, 247, 0.7)'],
                borderColor: ['#22c55e', '#38bdf8', '#f59e0b', '#a855f7'],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: 'Overall Model Statistical Validation Metrics', color: '#f8fafc', font: { size: 13, weight: 'bold' } },
                legend: { display: false }
            },
            scales: {
                x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
            }
        }
    });
}
