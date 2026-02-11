// ============================================
// Chart.js - Charting and Visualization
// ============================================

// Chart configuration helper
const ChartConfig = {
    colors: {
        primary: '#22c55e',
        secondary: '#3b82f6',
        danger: '#ef4444',
        warning: '#f59e0b',
        success: '#10b981',
        purple: '#b400ff',
        magenta: '#ff00ff'
    },
    
    themes: {
        dark: {
            backgroundColor: 'rgba(15, 23, 42, 0.8)',
            borderColor: 'rgba(55, 65, 81, 0.5)',
            textColor: '#f3f4f6',
            gridColor: 'rgba(75, 85, 99, 0.2)'
        }
    }
};

// Line Chart for daily trends
class TrendChart {
    constructor(canvasId, labels, data, label = 'Tests') {
        this.canvasId = canvasId;
        this.labels = labels;
        this.data = data;
        this.label = label;
        this.chart = null;
    }

    render() {
        const ctx = document.getElementById(this.canvasId);
        if (!ctx) return;

        const theme = ChartConfig.themes.dark;

        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.labels,
                datasets: [{
                    label: this.label,
                    data: this.data,
                    borderColor: ChartConfig.colors.primary,
                    backgroundColor: 'rgba(34, 197, 94, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 5,
                    pointBackgroundColor: ChartConfig.colors.primary,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointHoverRadius: 7,
                    pointHoverBackgroundColor: ChartConfig.colors.secondary
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            color: theme.textColor,
                            font: { size: 14, weight: 'bold' },
                            padding: 15
                        }
                    },
                    filler: {
                        propagate: true
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: theme.gridColor,
                            drawBorder: false
                        },
                        ticks: {
                            color: theme.textColor,
                            font: { size: 12 }
                        }
                    },
                    x: {
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            color: theme.textColor,
                            font: { size: 12 }
                        }
                    }
                }
            }
        });
    }

    destroy() {
        if (this.chart) {
            this.chart.destroy();
        }
    }

    update(labels, data) {
        if (!this.chart) return;
        this.chart.data.labels = labels;
        this.chart.data.datasets[0].data = data;
        this.chart.update();
    }
}

// Bar Chart for category breakdown
class BarChart {
    constructor(canvasId, labels, datasets) {
        this.canvasId = canvasId;
        this.labels = labels;
        this.datasets = datasets;
        this.chart = null;
    }

    render() {
        const ctx = document.getElementById(this.canvasId);
        if (!ctx) return;

        const theme = ChartConfig.themes.dark;
        const colors = [
            ChartConfig.colors.primary,
            ChartConfig.colors.secondary,
            ChartConfig.colors.magenta,
            ChartConfig.colors.warning
        ];

        const formattedDatasets = this.datasets.map((dataset, index) => ({
            label: dataset.label,
            data: dataset.data,
            backgroundColor: colors[index % colors.length],
            borderColor: 'rgba(255, 255, 255, 0.1)',
            borderWidth: 1,
            borderRadius: 8,
            hoverBackgroundColor: colors[index % colors.length],
            hoverBorderColor: 'rgba(255, 255, 255, 0.3)'
        }));

        this.chart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: this.labels,
                datasets: formattedDatasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                indexAxis: 'x',
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            color: theme.textColor,
                            font: { size: 14, weight: 'bold' },
                            padding: 15
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: theme.gridColor,
                            drawBorder: false
                        },
                        ticks: {
                            color: theme.textColor,
                            font: { size: 12 }
                        }
                    },
                    x: {
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            color: theme.textColor,
                            font: { size: 12 }
                        }
                    }
                }
            }
        });
    }

    destroy() {
        if (this.chart) {
            this.chart.destroy();
        }
    }
}

// Doughnut Chart for distribution
class DoughnutChart {
    constructor(canvasId, labels, data) {
        this.canvasId = canvasId;
        this.labels = labels;
        this.data = data;
        this.chart = null;
    }

    render() {
        const ctx = document.getElementById(this.canvasId);
        if (!ctx) return;

        const theme = ChartConfig.themes.dark;
        const colors = [
            ChartConfig.colors.primary,
            ChartConfig.colors.secondary,
            ChartConfig.colors.magenta,
            ChartConfig.colors.purple
        ];

        this.chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: this.labels,
                datasets: [{
                    data: this.data,
                    backgroundColor: colors.slice(0, this.data.length),
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 2,
                    hoverBorderColor: 'rgba(255, 255, 255, 0.3)',
                    hoverBorderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom',
                        labels: {
                            color: theme.textColor,
                            font: { size: 13, weight: 'bold' },
                            padding: 15
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: theme.textColor,
                        bodyColor: theme.textColor,
                        borderColor: ChartConfig.colors.primary,
                        borderWidth: 1,
                        padding: 12,
                        titleFont: { size: 14, weight: 'bold' },
                        bodyFont: { size: 13 }
                    }
                }
            }
        });
    }

    destroy() {
        if (this.chart) {
            this.chart.destroy();
        }
    }

    update(labels, data) {
        if (!this.chart) return;
        this.chart.data.labels = labels;
        this.chart.data.datasets[0].data = data;
        this.chart.update();
    }
}

// Radar Chart for performance metrics
class RadarChart {
    constructor(canvasId, labels, datasets) {
        this.canvasId = canvasId;
        this.labels = labels;
        this.datasets = datasets;
        this.chart = null;
    }

    render() {
        const ctx = document.getElementById(this.canvasId);
        if (!ctx) return;

        const theme = ChartConfig.themes.dark;
        const colors = [
            ChartConfig.colors.primary,
            ChartConfig.colors.secondary,
            ChartConfig.colors.magenta
        ];

        const formattedDatasets = this.datasets.map((dataset, index) => ({
            label: dataset.label,
            data: dataset.data,
            borderColor: colors[index % colors.length],
            backgroundColor: colors[index % colors.length] + '33',
            borderWidth: 2,
            pointRadius: 4,
            pointBackgroundColor: colors[index % colors.length],
            pointBorderColor: '#fff',
            pointBorderWidth: 2,
            pointHoverRadius: 6
        }));

        this.chart = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: this.labels,
                datasets: formattedDatasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        display: true,
                        labels: {
                            color: theme.textColor,
                            font: { size: 13, weight: 'bold' },
                            padding: 15
                        }
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        grid: {
                            color: theme.gridColor,
                            drawBorder: true,
                            borderColor: theme.borderColor
                        },
                        ticks: {
                            color: theme.textColor,
                            font: { size: 11 },
                            backdropColor: 'transparent'
                        }
                    }
                }
            }
        });
    }

    destroy() {
        if (this.chart) {
            this.chart.destroy();
        }
    }
}

// Chart manager for organizing multiple charts
class ChartManager {
    constructor() {
        this.charts = {};
    }

    add(name, chart) {
        if (this.charts[name]) {
            this.charts[name].destroy();
        }
        this.charts[name] = chart;
    }

    render(name) {
        if (this.charts[name]) {
            this.charts[name].render();
        }
    }

    renderAll() {
        Object.values(this.charts).forEach(chart => chart.render());
    }

    update(name, labels, data) {
        if (this.charts[name]) {
            this.charts[name].update(labels, data);
        }
    }

    destroyAll() {
        Object.values(this.charts).forEach(chart => chart.destroy());
        this.charts = {};
    }
}

// Initialize Chart.js with CDN fallback detection
function initializeCharts() {
    if (typeof Chart === 'undefined') {
        console.error('Chart.js library not loaded. Please ensure Chart.js is included.');
        return false;
    }
    return true;
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        TrendChart,
        BarChart,
        DoughnutChart,
        RadarChart,
        ChartManager,
        ChartConfig,
        initializeCharts
    };
}
