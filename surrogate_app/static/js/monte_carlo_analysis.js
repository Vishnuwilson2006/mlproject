/**
 * monte_carlo_analysis.js
 * CircuitAI - Module 2: Component Tolerance & Monte Carlo Analysis Chart Rendering
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
        renderMonteCarloCharts(initialData);
    } catch (e) {
        console.error("Error parsing Monte Carlo data:", e);
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
                submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Simulating...';
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
                    submitBtn.innerHTML = '<i class="bi bi-dice-5-fill me-1"></i> Run Monte Carlo Simulation';
                }
                if (data && data.success) {
                    updateMonteCarloUI(data);
                    renderMonteCarloCharts(data);
                }
            })
            .catch(err => {
                console.error("Error running Monte Carlo simulation:", err);
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = '<i class="bi bi-dice-5-fill me-1"></i> Run Monte Carlo Simulation';
                }
            });
        });
    }

    // Attach Download PNG listeners
    document.querySelectorAll(".download-chart-btn").forEach(btn => {
        btn.addEventListener("click", function () {
            const canvasId = this.getAttribute("data-chart");
            downloadChartPNG(canvasId, "Monte_Carlo_Analysis_Chart.png");
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

function updateMonteCarloUI(data) {
    const scoreElem = document.getElementById("robustnessScoreVal");
    if (scoreElem) scoreElem.innerText = `${data.robustness_score}%`;

    const expElem = document.getElementById("robustnessExpText");
    if (expElem) expElem.innerText = data.robustness_explanation;
}

function renderMonteCarloCharts(data) {
    if (!data || !data.outputs_analysis || data.outputs_analysis.length === 0) {
        console.warn("No output analysis data available for Monte Carlo.");
        return;
    }

    const outputs = data.outputs_analysis;
    const out1 = outputs[0];
    const out2 = outputs[1] || outputs[0];
    const out3 = outputs[2] || outputs[0];

    // 1. Gain Distribution Histogram (Primary Output)
    const bins1 = out1.hist_bins || [];
    const counts1 = (out1.hist_counts || []).map(v => safeValue(v));

    createChart('chartHistGain', {
        type: 'bar',
        data: {
            labels: bins1,
            datasets: [{
                label: `${out1.label} (${out1.unit})`,
                data: counts1,
                backgroundColor: 'rgba(34, 197, 94, 0.7)',
                borderColor: '#22c55e',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: `${out1.label} Distribution Histogram (N=${data.n_simulations})`, color: '#f8fafc', font: { size: 13, weight: 'bold' } },
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        title: (items) => `${out1.label}: ${items[0].label} ${out1.unit}`,
                        label: (item) => `Simulations Count: ${item.raw}`
                    }
                }
            },
            scales: {
                x: { title: { display: true, text: `${out1.label} (${out1.unit})`, color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                y: { title: { display: true, text: 'Frequency (Simulations)', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
            }
        }
    });

    // 2. Cutoff Frequency Distribution (Secondary Output)
    const bins2 = out2.hist_bins || [];
    const counts2 = (out2.hist_counts || []).map(v => safeValue(v));

    createChart('chartHistFc', {
        type: 'bar',
        data: {
            labels: bins2,
            datasets: [{
                label: `${out2.label} (${out2.unit})`,
                data: counts2,
                backgroundColor: 'rgba(56, 189, 248, 0.7)',
                borderColor: '#38bdf8',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: `${out2.label} Distribution Histogram`, color: '#f8fafc', font: { size: 13, weight: 'bold' } },
                legend: { display: false }
            },
            scales: {
                x: { title: { display: true, text: `${out2.label} (${out2.unit})`, color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                y: { title: { display: true, text: 'Frequency', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
            }
        }
    });

    // 3. Phase Margin / 3rd Output Distribution
    const bins3 = out3.hist_bins || [];
    const counts3 = (out3.hist_counts || []).map(v => safeValue(v));

    createChart('chartHistPm', {
        type: 'line',
        data: {
            labels: bins3,
            datasets: [{
                label: `${out3.label} (${out3.unit}) Density`,
                data: counts3,
                borderColor: '#c084fc',
                backgroundColor: 'rgba(192, 132, 252, 0.2)',
                borderWidth: 2,
                fill: true,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: `${out3.label} Distribution Density`, color: '#f8fafc', font: { size: 13, weight: 'bold' } },
                legend: { display: false }
            },
            scales: {
                x: { title: { display: true, text: `${out3.label} (${out3.unit})`, color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                y: { title: { display: true, text: 'Simulations Count', color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
            }
        }
    });

    // 4. Box Plot (Min, P25, Median, P75, Max)
    const boxLabels = outputs.map(o => o.label);
    const boxMedians = outputs.map(o => safeValue(o.median));
    const boxP25 = outputs.map(o => safeValue(o.p25 || o.mean * 0.9));
    const boxP75 = outputs.map(o => safeValue(o.p75 || o.mean * 1.1));

    createChart('chartBoxPlot', {
        type: 'bar',
        data: {
            labels: boxLabels,
            datasets: [
                {
                    label: '25th Percentile (P25)',
                    data: boxP25,
                    backgroundColor: 'rgba(56, 189, 248, 0.6)'
                },
                {
                    label: 'Median Value',
                    data: boxMedians,
                    backgroundColor: 'rgba(34, 197, 94, 0.8)'
                },
                {
                    label: '75th Percentile (P75)',
                    data: boxP75,
                    backgroundColor: 'rgba(245, 158, 11, 0.6)'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: 'Statistical Quantile Box Plot Overview (P25 - Median - P75)', color: '#f8fafc', font: { size: 13, weight: 'bold' } },
                legend: { labels: { color: '#94a3b8' } }
            },
            scales: {
                x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
            }
        }
    });

    // 5. Component Tolerance vs Output Scatter
    const scatterData = data.tolerance_scatter || { points: [], comp_name: 'Component', output_name: 'Output', output_unit: '' };
    const points = (scatterData.points || []).map(p => ({ x: safeValue(p.x), y: safeValue(p.y) }));

    createChart('chartScatterTolerance', {
        type: 'scatter',
        data: {
            datasets: [{
                label: `${scatterData.comp_name} Variation vs ${scatterData.output_name}`,
                data: points,
                backgroundColor: 'rgba(168, 85, 247, 0.7)',
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: `Component Perturbation (%) vs ${scatterData.output_name}`, color: '#f8fafc', font: { size: 13, weight: 'bold' } },
                legend: { labels: { color: '#94a3b8' } },
                tooltip: {
                    callbacks: {
                        label: (item) => `${scatterData.comp_name} Δ: ${item.parsed.x}%, ${scatterData.output_name}: ${item.parsed.y} ${scatterData.output_unit}`
                    }
                }
            },
            scales: {
                x: { title: { display: true, text: `${scatterData.comp_name} Variation (%)`, color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                y: { title: { display: true, text: `${scatterData.output_name} (${scatterData.output_unit})`, color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
            }
        }
    });

    // 6. Target Achievement Doughnut Chart
    const ta = data.target_achievement || { pass_pct: data.robustness_score || 95, fail_pct: 5 };

    createChart('chartDoughnutTarget', {
        type: 'doughnut',
        data: {
            labels: ['Satisfies Target Specs (Pass)', 'Fails Target Specs'],
            datasets: [{
                data: [safeValue(ta.pass_pct, 95), safeValue(ta.fail_pct, 5)],
                backgroundColor: ['#22c55e', '#ef4444'],
                borderColor: ['#15803d', '#b91c1c'],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: `Target Achievement Yield (${ta.pass_pct}% Pass Rate)`, color: '#f8fafc', font: { size: 13, weight: 'bold' } },
                legend: { labels: { color: '#94a3b8' } }
            }
        }
    });

    // 7. Robustness Cumulative Distribution Function (CDF)
    const cdfX = out1.cdf_x || [];
    const cdfY = (out1.cdf_y || []).map(v => safeValue(v));

    createChart('chartRobustnessCDF', {
        type: 'line',
        data: {
            labels: cdfX,
            datasets: [{
                label: `Cumulative Yield Percentage (%)`,
                data: cdfY,
                borderColor: '#fbbf24',
                backgroundColor: 'rgba(251, 191, 36, 0.1)',
                borderWidth: 2,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: { display: true, text: `Cumulative Probability Yield (CDF) for ${out1.label}`, color: '#f8fafc', font: { size: 13, weight: 'bold' } },
                legend: { labels: { color: '#94a3b8' } }
            },
            scales: {
                x: { title: { display: true, text: `${out1.label} (${out1.unit})`, color: '#94a3b8' }, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } },
                y: { title: { display: true, text: 'Cumulative %', color: '#94a3b8' }, min: 0, max: 100, ticks: { color: '#94a3b8' }, grid: { color: 'rgba(255, 255, 255, 0.05)' } }
            }
        }
    });
}
