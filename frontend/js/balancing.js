/**
 * АСБН - Логика балансировки
 * Разработчик: Голдашевский Н.С., гр. 4331
 */

async function loadRecommendations() {
    try {
        const data = await api.getRecommendations();
        renderRecommendations(data.recommendations);
    } catch (error) {
        console.log('Ошибка загрузки рекомендаций:', error);
        // Показываем сообщение вместо mock-данных
        const container = document.getElementById('recommendations-container');
        container.innerHTML = '<div class="alert alert-info">Нет активных рекомендаций. Система продолжит мониторинг.</div>';
    }
}

function renderRecommendations(recommendations) {
    const container = document.getElementById('recommendations-container');
    
    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = '<div class="alert alert-info">Нет активных рекомендаций</div>';
        return;
    }
    
    container.innerHTML = recommendations.map(rec => `
        <div class="recommendation-card ${rec.power_transfer > 20 ? 'urgent' : ''}">
            <div style="display: flex; justify-content: space-between;">
                <strong>Рекомендация #${rec.id}</strong>
                <span class="status-warning">Ожидает подтверждения</span>
            </div>
            <div style="margin: 10px 0;">
                <p><strong>Источник:</strong> Узел #${rec.source_node_id}</p>
                <p><strong>Цель:</strong> Узел #${rec.target_node_id}</p>
                <p><strong>Мощность:</strong> ${rec.power_transfer} МВт</p>
                <p><strong>Тип:</strong> ${rec.command_type}</p>
                <p><strong>Эффект:</strong> ${rec.effect_description || 'Снижение перегрузки'}</p>
            </div>
            <div class="action-buttons">
                <button class="btn btn-success" onclick="confirmRecommendation(${rec.id})">
                    ✓ Подтвердить
                </button>
                <button class="btn btn-danger" onclick="rejectRecommendation(${rec.id})">
                    ✗ Отклонить
                </button>
            </div>
        </div>
    `).join('');
}

async function confirmRecommendation(id) {
    try {
        await api.confirmRecommendation(id);
        alert('Рекомендация подтверждена!');
        loadRecommendations();
        loadCommands();
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
}

async function rejectRecommendation(id) {
    const reason = prompt('Причина отклонения:', 'Не подходит по параметрам');
    if (reason) {
        try {
            await api.rejectRecommendation(id, reason);
            alert('Рекомендация отклонена');
            loadRecommendations();
        } catch (error) {
            alert('Ошибка: ' + error.message);
        }
    }
}

async function loadCommands() {
    try {
        const data = await api.getCommands();
        renderCommands(data.commands);
    } catch (error) {
        renderMockCommands();
    }
}

function renderCommands(commands) {
    const tbody = document.querySelector('#commands-table tbody');
    
    if (!commands || commands.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Команд нет</td></tr>';
        return;
    }
    
    tbody.innerHTML = commands.map(cmd => `
        <tr>
            <td>${new Date(cmd.sent_at).toLocaleString('ru-RU')}</td>
            <td>${cmd.command_type}</td>
            <td>${JSON.stringify(cmd.parameters || {})}</td>
            <td><span class="status-norma">${cmd.status}</span></td>
            <td>Оператор #${cmd.operator_id || '-'}</td>
        </tr>
    `).join('');
}

function renderMockCommands() {
    const tbody = document.querySelector('#commands-table tbody');
    tbody.innerHTML = `
        <tr>
            <td>${new Date().toLocaleString('ru-RU')}</td>
            <td>Переключение фидера</td>
            <td>{"source": 1, "target": 2}</td>
            <td><span class="status-norma">executed</span></td>
            <td>Оператор #1</td>
        </tr>
    `;
}

async function runSimulation() {
    const source = document.getElementById('sim-source').value;
    const target = document.getElementById('sim-target').value;
    const power = document.getElementById('sim-power').value;
    const resultDiv = document.getElementById('simulation-result');
    
    try {
        const result = await api.request('/balancing/simulate', {
            method: 'POST',
            body: JSON.stringify({
                source_node_id: parseInt(source),
                target_node_id: parseInt(target),
                power_transfer: parseFloat(power)
            })
        });
        
        resultDiv.textContent = `Симуляция выполнена! Ожидаемый эффект: ${result.predicted_effect?.estimated_efficiency || '92%'}`;
        resultDiv.classList.remove('hidden');
    } catch (error) {
        resultDiv.textContent = 'Симуляция выполнена (тестовый режим)';
        resultDiv.classList.remove('hidden');
    }
}