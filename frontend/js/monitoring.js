/**
 * АСБН - Логика панели мониторинга
 * Разработчик: Голдашевский Н.С., гр. 4331
 */

let measurementsChart = null;

async function loadMonitoringData() {
    try {
        // Загрузка статуса сети
        const status = await api.getNodeStatus();
        updateStatusCards(status);
        
        // Загрузка топологии
        const topology = await api.getTopology();
        renderNodes(topology.nodes);
        
        // Загрузка измерений
        const measurements = await api.getMeasurements(null, 50);
        renderMeasurementsChart(measurements.measurements);
        
        // Загрузка инцидентов
        const incidents = await api.getIncidents(10);
        renderIncidents(incidents.incidents);
        
    } catch (error) {
        console.error('Ошибка загрузки данных:', error);
        showAlert('Ошибка загрузки данных мониторинга', 'error');
    }
}

function updateStatusCards(status) {
    document.getElementById('total-nodes').textContent = status.total_nodes || 0;
    
    const dist = status.status_distribution || {};
    document.getElementById('norma-nodes').textContent = dist.norma || 0;
    document.getElementById('warning-nodes').textContent = dist.warning || 0;
    document.getElementById('overload-nodes').textContent = 
        (dist.overload || 0) + (dist.emergency || 0);
}

function renderNodes(nodes) {
    const container = document.getElementById('nodes-container');
    container.innerHTML = '';
    
    nodes.forEach(node => {
        const statusClass = node.status === 'norma' ? '' : 
                           node.status === 'warning' ? 'warning' : 'overload';
        
        const card = document.createElement('div');
        card.className = `node-card ${statusClass}`;
        card.innerHTML = `
            <div style="font-weight: 600;">${node.name}</div>
            <div style="font-size: 12px; color: #718096;">${node.type}</div>
            <div style="margin-top: 10px;">
                <span class="status-${node.status}">● ${getStatusText(node.status)}</span>
            </div>
            <div style="font-size: 13px; margin-top: 5px;">
                Напряжение: ${node.voltage || '-'} кВ<br>
                Мощность: ${node.power || '-'} МВт
            </div>
        `;
        container.appendChild(card);
    });
}

function getStatusText(status) {
    const map = {
        'norma': 'Норма',
        'warning': 'Предупреждение',
        'overload': 'Перегрузка',
        'emergency': 'Авария',
        'offline': 'Отключено'
    };
    return map[status] || status;
}

function renderMeasurementsChart(measurements) {
    const ctx = document.getElementById('measurements-chart').getContext('2d');
    
    // Подготовка данных
    const labels = measurements.slice(0, 20).map(m => 
        new Date(m.timestamp).toLocaleTimeString('ru-RU', {hour: '2-digit', minute:'2-digit'})
    );
    const powerData = measurements.slice(0, 20).map(m => m.active_power || 0);
    
    if (measurementsChart) {
        measurementsChart.destroy();
    }
    
    measurementsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Активная мощность (МВт)',
                data: powerData,
                borderColor: '#4299e1',
                backgroundColor: 'rgba(66, 153, 225, 0.1)',
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

function renderIncidents(incidents) {
    const tbody = document.querySelector('#incidents-table tbody');
    tbody.innerHTML = '';
    
    if (!incidents || incidents.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center">Инцидентов нет</td></tr>';
        return;
    }
    
    incidents.forEach(inc => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${new Date(inc.timestamp).toLocaleString('ru-RU')}</td>
            <td><span class="status-${inc.severity === 'critical' ? 'overload' : 'warning'}">${inc.type}</span></td>
            <td>${inc.description}</td>
            <td>${inc.severity}</td>
        `;
        tbody.appendChild(row);
    });
}

function showAlert(message, type = 'info') {
    // Простая реализация уведомлений
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// Автообновление каждые 60 секунд
setInterval(() => {
    if (checkAuth()) {
        loadMonitoringData();
    }
}, 60000);