/**
 * АСБН - Логика уведомлений
 * Разработчик: Голдашевский Н.С., гр. 4331
 */

async function loadNotifications() {
    const filter = document.getElementById('filter-type').value;
    
    try {
        const data = await api.getNotifications(50);
        renderNotifications(data.notifications, filter);
    } catch (error) {
        renderMockNotifications(filter);
    }
}

function renderNotifications(notifications, filter = 'all') {
    const container = document.getElementById('notifications-container');
    
    let filtered = notifications;
    if (filter !== 'all') {
        filtered = notifications.filter(n => n.type === filter);
    }
    
    if (!filtered || filtered.length === 0) {
        container.innerHTML = '<div class="alert alert-info">Уведомлений нет</div>';
        return;
    }
    
    container.innerHTML = filtered.map(n => `
        <div class="notification-item ${n.type} ${n.is_read ? 'read' : ''}">
            <div class="notification-header">
                <strong>${getNotificationTypeText(n.type)}</strong>
                <span class="notification-time">${new Date(n.created_at).toLocaleString('ru-RU')}</span>
            </div>
            <div>${n.message}</div>
            <div style="margin-top: 10px; font-size: 12px; color: #718096;">
                Канал: ${n.channel} | Статус: ${n.status}
            </div>
            ${!n.is_read ? `<button class="btn btn-primary mt-1" onclick="markRead(${n.id})">Отметить как прочитанное</button>` : ''}
        </div>
    `).join('');
}

function renderMockNotifications(filter = 'all') {
    const container = document.getElementById('notifications-container');
    const mockData = [
        {
            id: 1,
            type: 'alert',
            message: 'Перегрузка узла ПС-2 Центральная: 97% от номинала',
            channel: 'interface',
            status: 'sent',
            created_at: new Date().toISOString(),
            is_read: false
        },
        {
            id: 2,
            type: 'warning',
            message: 'Прогнозируемая перегрузка через 2 часа: ПС-3 Южная',
            channel: 'interface',
            status: 'sent',
            created_at: new Date(Date.now() - 3600000).toISOString(),
            is_read: false
        },
        {
            id: 3,
            type: 'info',
            message: 'Рекомендация по балансировке #1 подтверждена диспетчером',
            channel: 'interface',
            status: 'delivered',
            created_at: new Date(Date.now() - 7200000).toISOString(),
            is_read: true
        }
    ];
    
    let filtered = mockData;
    if (filter !== 'all') {
        filtered = mockData.filter(n => n.type === filter);
    }
    
    renderNotifications(filtered, 'all');
}

function getNotificationTypeText(type) {
    const map = {
        'info': 'ℹ️ Информационное',
        'warning': '⚠️ Предупреждение',
        'alert': '🚨 Аварийное'
    };
    return map[type] || type;
}

async function markRead(id) {
    try {
        await api.markNotificationRead(id);
        loadNotifications();
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
}

async function markAllRead() {
    const items = document.querySelectorAll('.notification-item:not(.read)');
    for (let item of items) {
        // В прототипе просто визуально отмечаем
        item.classList.add('read');
    }
    alert('Все уведомления отмечены как прочитанные');
}