/**
 * active_learning.js
 * CircuitAI - Module 3: Active Learning / Smart Dataset Expansion Chart Rendering
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
        renderActiveLearningCharts(initialData);
    } catch (e) {
        console.error("Error parsing Active Learning data:", e);
    }

    // Attach AJAX form handler if present
    const form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault();
            const formData = new FormData(form);
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Retraining...';
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
                    submitBtn.innerHTML = '<i class="bi bi-play-fill me-1"></i> Execute Active Learning Retraining';
                }
                if (data && data.success) {
                    updateActiveLearningUI(data);
                    renderActiveLearningCharts(data);
                }
            })
            .catch(err => {
                console.error("Error running Active Learning:", err);
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="bi bi-play-fill me-1"></i> Execute Active Learning Retraining';
                }
            });
        });
    }

    // Attach Download PNG listeners
    document.querySelectorAll(".download-chart-btn").forEach(btn => {
        btn.addEventListener("click", function () {
            const canvasId = this.getAttribute("data-chart");
            downloadChartPNG(canvasId, "Active_Learning_Chart.png");
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

function updateActiveLearningUI(data) {
    const r2Elem = document.getElementById("r2ScoreText");
    if (r2Elem) r2Elem.innerText = `${data.initial_r2} → ${data.final_r2}`;

    const maeElem = document.getElementById("maeErrorText");
    if (maeElem) maeElem.innerText = `${data.initial_mae} → ${data.final_mae}`;

    const impElem = document.getElementById("improvementPctText");
    if (impElem) impElem.innerText = `+${data.improvement_pct}%`;

    const insElem = document.getElementById("researchInsightText");
    if (insElem) insElem.innerText = data.research_insight;
}

function renderActiveLearningCharts(data) {
    if (!data || !data.graph_data) {
        console.warn("No graph data available for Active Learning.");
        return;
    }

    const gd = data.graph_data;
    const sizes = gd.dataset_sizes || [50, 60, 70, 80, 90, 100];
    const iterLabels = gd.iter_labels || sizes.map((_, i) => `Iter ${i}`);

    // 1. Dataset Size vs R²
    const r2Active = (gd.r2_active || []).map(v => safeValue(v));

    createChart('chartR2Progression', {
        type: 'line',
        data: {
            labels: sizes,
            datasets: [{
                label: 'R² Accuracy Score',
                data: r2Active,
                borderColor: '#22c55e',
                backgroundColor: 'rgba(34, 197, 94, 0.15)',
                borderWidth: 2,
                fill: true,
                tension: 0.3,
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: 'Dataset Size vs R² Accuracy Score Progression', color: '#f8fafc', font: { size: 13, weight: 'bold' } },
                legend: { labels: { color: '#94a3b8' } }
            },
            scales: {
                x: { title: { display: true, text: 'Dataset Size (Samples)', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                y: { title: { display: true, text: 'R² Score', color: '#94a3b8' }, min: 0.8, max: 1.0, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
            }
        }
    });

    // 2. Dataset Size vs MAE
    const maeActive = (gd.mae_active || []).map(v => safeValue(v));

    createChart('chartMAEProgression', {
        type: 'line',
        data: {
            labels: sizes,
            datasets: [{
                label: 'MAE (Mean Absolute Error)',
                data: maeActive,
                borderColor: '#f43f5e',
                backgroundColor: 'rgba(244, 63, 94, 0.15)',
                borderWidth: 2,
                fill: true,
                tension: 0.3,
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: 'Dataset Size vs MAE Reduction Curve', color: '#f8fafc', font: { size: 13, weight: 'bold' } },
                legend: { labels: { color: '#94a3b8' } }
            },
            scales: {
                x: { title: { display: true, text: 'Dataset Size (Samples)', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                y: { title: { display: true, text: 'MAE Error', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
            }
        }
    });

    // 3. Active Learning vs Random Sampling Comparison
    const r2Random = (gd.r2_random || []).map(v => safeValue(v));

    createChart('chartCompareSampling', {
        type: 'line',
        data: {
            labels: iterLabels,
            datasets: [
                {
                    label: `Smart Active Learning (${data.sampling_strategy || 'Uncertainty'})`,
                    data: r2Active,
                    borderColor: '#f59e0b',
                    backgroundColor: '#f59e0b',
                    borderWidth: 3,
                    pointRadius: 5,
                    fill: false
                },
                {
                    label: 'Traditional Random Dataset Expansion',
                    data: r2Random,
                    borderColor: '#94a3b8',
                    borderDash: [5, 5],
                    borderWidth: 2,
                    pointRadius: 3,
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: 'Smart Active Learning vs Traditional Random Sampling Efficiency', color: '#f8fafc', font: { size: 13, weight: 'bold' } },
                legend: { labels: { color: '#94a3b8' } }
            },
            scales: {
                x: { title: { display: true, text: 'Retraining Iterations', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                y: { title: { display: true, text: 'R² Accuracy Score', color: '#94a3b8' }, min: 0.8, max: 1.0, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
            }
        }
    });

    // 4. Error Before vs After Active Learning
    const errHist = gd.error_histogram || { bins: ['-0.5', '0.0', '0.5'], counts_before: [10, 30, 10], counts_after: [2, 45, 3] };
    const errBins = errHist.bins || [];
    const countsBefore = (errHist.counts_before || []).map(v => safeValue(v));
    const countsAfter = (errHist.counts_after || []).map(v => safeValue(v));

    createChart('chartErrorDistribution', {
        type: 'bar',
        data: {
            labels: errBins,
            datasets: [
                {
                    label: 'Residual Error BEFORE Active Retraining',
                    data: countsBefore,
                    backgroundColor: 'rgba(244, 63, 94, 0.6)',
                    borderColor: '#f43f5e',
                    borderWidth: 1
                },
                {
                    label: 'Residual Error AFTER Active Retraining',
                    data: countsAfter,
                    backgroundColor: 'rgba(34, 197, 94, 0.7)',
                    borderColor: '#22c55e',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: 'Surrogate Prediction Error Distribution (Before vs After Retraining)', color: '#f8fafc', font: { size: 13, weight: 'bold' } },
                legend: { labels: { color: '#94a3b8' } }
            },
            scales: {
                x: { title: { display: true, text: 'Residual Error Bin', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                y: { title: { display: true, text: 'Frequency Count', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
            }
        }
    });

    // 5. Uncertainty Map
    const uMapPts = (gd.uncertainty_map || []).map(p => ({
        x: safeValue(p.x),
        y: safeValue(p.y),
        r: Math.max(3, safeValue(p.uncertainty * 15, 6))
    }));

    createChart('chartUncertaintyMap', {
        type: 'bubble',
        data: {
            datasets: [{
                label: 'Sample Uncertainty Map (Bubble Size = Model Variance)',
                data: uMapPts,
                backgroundColor: 'rgba(168, 85, 247, 0.6)',
                borderColor: '#a855f7'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: 'Circuit Operational Feature Space Uncertainty Map', color: '#f8fafc', font: { size: 13, weight: 'bold' } },
                legend: { labels: { color: '#94a3b8' } }
            },
            scales: {
                x: { title: { display: true, text: 'Circuit Component Parameter (Feature 1)', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                y: { title: { display: true, text: 'Operational Parameter (Feature 2)', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
            }
        }
    });

    // 6. Training Sample Selection Visualization
    const samples = gd.sample_selection || { initial_samples: [], queried_samples: [], pool_samples: [] };
    const initPts = (samples.initial_samples || []).map(p => ({ x: safeValue(p.x), y: safeValue(p.y) }));
    const queryPts = (samples.queried_samples || []).map(p => ({ x: safeValue(p.x), y: safeValue(p.y) }));
    const poolPts = (samples.pool_samples || []).map(p => ({ x: safeValue(p.x), y: safeValue(p.y) }));

    createChart('chartSampleSelection', {
        type: 'scatter',
        data: {
            datasets: [
                {
                    label: `Initial Baseline Dataset (${data.initial_size} Samples)`,
                    data: initPts,
                    backgroundColor: '#64748b',
                    pointRadius: 5
                },
                {
                    label: `Queried Active Learning Samples (${data.added_samples} Added)`,
                    data: queryPts,
                    backgroundColor: '#f59e0b',
                    borderColor: '#ffffff',
                    borderWidth: 1,
                    pointRadius: 7
                },
                {
                    label: 'Unlabeled Candidate Pool',
                    data: poolPts,
                    backgroundColor: 'rgba(56, 189, 248, 0.3)',
                    pointRadius: 3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: 'Active Query Sample Selection Strategy Visualization', color: '#f8fafc', font: { size: 13, weight: 'bold' } },
                legend: { labels: { color: '#94a3b8' } }
            },
            scales: {
                x: { title: { display: true, text: 'Normalized Feature X', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                y: { title: { display: true, text: 'Normalized Feature Y', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
            }
        }
    });
}
