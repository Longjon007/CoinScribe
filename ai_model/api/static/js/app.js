document.addEventListener('DOMContentLoaded', () => {
    // Navigation Logic
    const navItems = document.querySelectorAll('.nav-item');
    const views = document.querySelectorAll('.view');
    const pageHeader = document.getElementById('page-header');

    // Set current date
    const dateOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    document.getElementById('current-date').textContent = new Date().toLocaleDateString('en-US', dateOptions);

    navItems.forEach(item => {
        item.addEventListener('click', () => {
            const tabName = item.getAttribute('data-tab');

            // Update Nav
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');

            // Update View
            views.forEach(view => view.classList.remove('active'));
            document.getElementById(`${tabName}-view`).classList.add('active');

            // Update Header
            pageHeader.textContent = item.querySelector('span').textContent;

            // Load specific data if needed
            if(tabName === 'market') loadMarketData();
            if(tabName === 'model') loadModelInfo();
        });
    });

    // Initialize Chart
    const ctx = document.getElementById('mainChart').getContext('2d');
    let mainChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'AI Composite Index',
                data: [65, 59, 80, 81, 56, 55, 40],
                fill: true,
                backgroundColor: 'rgba(99, 102, 241, 0.2)',
                borderColor: 'rgb(99, 102, 241)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: '#94a3b8' }
                }
            },
            scales: {
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8' }
                }
            }
        }
    });

    // Mock Data Loading for Dashboard
    fetchDashboardData();

    // Prediction Logic
    const predictBtn = document.getElementById('run-prediction-btn');
    predictBtn.addEventListener('click', async () => {
        const selectedAssets = Array.from(document.querySelectorAll('input[type="checkbox"]:checked'))
            .map(cb => cb.value);

        predictBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Analyzing...';

        try {
            const response = await fetch('/api/predict/indices', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ symbols: selectedAssets })
            });

            const data = await response.json();
            displayPredictionResults(data);

        } catch (error) {
            console.error('Prediction failed:', error);
            // Fallback for demo if backend not fully ready
            setTimeout(() => {
                displayPredictionResults({
                    indices: [0.75, 0.82, 0.65, 0.90, 0.55],
                    confidence: 0.89,
                    timestamp: new Date().toISOString()
                });
            }, 1000);
        } finally {
            predictBtn.innerHTML = '<i class="fa-solid fa-bolt"></i> Run Analysis';
        }
    });

    function displayPredictionResults(data) {
        const container = document.getElementById('prediction-results');
        container.classList.remove('hidden');

        const html = `
            <div class="glass-panel" style="margin-top: 1.5rem">
                <div class="panel-header">
                    <h2>Analysis Results</h2>
                    <span class="trend up">Confidence: ${(data.confidence * 100).toFixed(1)}%</span>
                </div>
                <div class="stats-grid">
                    ${data.indices.slice(0, 3).map((val, idx) => `
                        <div class="stat-card">
                            <div class="stat-info">
                                <h3>Index Sector ${idx + 1}</h3>
                                <p class="value">${val.toFixed(2)}</p>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        container.innerHTML = html;
    }

    async function fetchDashboardData() {
        // Mock data update
        setTimeout(() => {
            document.getElementById('btc-index').textContent = '42,150';
            document.getElementById('eth-index').textContent = '2,240';
            document.getElementById('ai-confidence').textContent = '87%';
        }, 500);
    }

    async function loadMarketData() {
        const tbody = document.querySelector('#market-table tbody');
        tbody.innerHTML = '<tr><td colspan="5">Loading live data...</td></tr>';

        try {
            // Real fetch
            // const res = await fetch('/api/data/fetch', { ... });

            // Mock for demo
            setTimeout(() => {
                const assets = [
                    { symbol: 'BTC', price: '$42,150', change: '+2.4%', vol: '$24B', sent: 'Bullish' },
                    { symbol: 'ETH', price: '$2,240', change: '-0.8%', vol: '$12B', sent: 'Neutral' },
                    { symbol: 'SOL', price: '$98.50', change: '+5.1%', vol: '$3B', sent: 'Bullish' },
                    { symbol: 'ADA', price: '$0.52', change: '-1.2%', vol: '$800M', sent: 'Bearish' },
                ];

                tbody.innerHTML = assets.map(asset => `
                    <tr>
                        <td style="font-weight: 600">${asset.symbol}</td>
                        <td>${asset.price}</td>
                        <td style="color: ${asset.change.includes('+') ? 'var(--success)' : 'var(--danger)'}">${asset.change}</td>
                        <td>${asset.vol}</td>
                        <td><span class="trend ${asset.sent === 'Bullish' ? 'up' : asset.sent === 'Bearish' ? 'down' : 'neutral'}">${asset.sent}</span></td>
                    </tr>
                `).join('');
            }, 800);
        } catch(e) {
            tbody.innerHTML = '<tr><td colspan="5">Failed to load data</td></tr>';
        }
    }

    async function loadModelInfo() {
        const content = document.getElementById('model-info-content');
        try {
            const response = await fetch('/api/model/info');
            const data = await response.json();
            content.textContent = JSON.stringify(data, null, 2);
        } catch(e) {
            content.textContent = "Error loading model info. Backend might be offline.";
        }
    }
});
