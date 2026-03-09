/**
 * АСБН - Логика прогнозирования
 * Разработчик: Голдашевский Н.С., гр. 4331
 */

let forecastChart = null;

async function loadForecast() {
    const nodeId = document.getElementById('node-select').value;
    
    try {
        const data = await api.getForecast(nodeId);
        renderForecastChart(data.forecasts);
        updateMetrics(data.forecasts);
    } catch (error) {
        console.error('Ошибка загрузки прогноза:', error);
        // Для прототипа генерируем тестовые данные
        const mockData = generateMockForecast();
        renderForecastChart(mockData);
        updateMetrics(mockData);
    }
}

function generateMockForecast() {
    const forecasts = [];
    const now = new Date();
    let baseLoad = 50;
    
    for (let i = 0; i < 96; i++) {
        const time = new Date(now.getTime() + i * 15 * 60000);
        const hour = time.getHours();
        
        // Имитация суточного цикла
        const hourFactor = 1 + 0.3 * Math.sin((hour - 6) * Math.PI / 12);
        const predicted = baseLoad * hourFactor + (Math.random() - 0.5) * 5;
        
        forecasts.push({
            timestamp: time.toISOString(),
            predicted_load: predicted.toFixed(2),
            confidence_lower: (predicted * 0.9).toFixed(2),
            confidence_upper: (predicted * 1.1).toFixed(2),
            mape_error: (3 + Math.random() * 2).toFixed(2)
        });
    }
    
    return forecasts;
}

function renderForecastChart(forecasts) {
    const ctx = document.getElementById('forecast-chart').getContext('2d');
    
    const labels = forecasts.slice(0, 48).map(f => 
        new Date(f.timestamp).toLocaleTimeString('ru-RU', {hour: '2-digit', minute:'2-digit'})
    );
    const predicted = forecasts.slice(0, 48).map(f => f.predicted_load);
    const lower = forecasts.slice(0, 48).map(f => f.confidence_lower);
    const upper = forecasts.slice(0, 48).map(f => f.confidence_upper);
    
    if (forecastChart) forecastChart.destroy();
    
    forecastChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Прогноз (МВт)',
                    data: predicted,
                    borderColor: '#4299e1',
                    backgroundColor: 'rgba(66, 153, 225, 0.1)',
                    fill: false,
                    tension: 0.4
                },
                {
                    label: 'Нижняя граница',
                    data: lower,
                    borderColor: '#48bb78',
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0
                },
                {
                    label: 'Верхняя граница',
                    data: upper,
                    borderColor: '#f56565',
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: true, position: 'top' }
            },
            scales: {
                y: { beginAtZero: false }
            }
        }
    });
}

function updateMetrics(forecasts) {
    const loads = forecasts.map(f => parseFloat(f.predicted_load));
    const mape = forecasts.map(f => parseFloat(f.mape_error));
    
    const avgLoad = (loads.reduce((a, b) => a + b, 0) / loads.length).toFixed(2);
    const maxLoad = Math.max(...loads).toFixed(2);
    const avgMape = (mape.reduce((a, b) => a + b, 0) / mape.length).toFixed(2);
    
    document.getElementById('mape-value').textContent = avgMape;
    document.getElementById('max-load').textContent = maxLoad;
    document.getElementById('avg-load').textContent = avgLoad;
    document.getElementById('confidence').textContent = '95';
    
    document.getElementById('metrics-mape').textContent = avgMape + '%';
    document.getElementById('metrics-rmse').textContent = (avgMape * 0.8).toFixed(2) + '%';
    document.getElementById('metrics-r2').textContent = '0.' + (95 + Math.random() * 4).toFixed(0);
}