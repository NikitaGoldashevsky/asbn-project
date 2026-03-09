/**
 * АСБН - Логика админ-панели
 * Разработчик: Голдашевский Н.С., гр. 4331
 */

async function loadAdminData() {
    loadUsers();
    loadSystemStatus();
    loadCommandsLog();
    loadSystemLogs();
}

async function loadUsers() {
    try {
        const data = await api.getUsers();
        renderUsers(data.users);
    } catch (error) {
        renderMockUsers();
    }
}

function renderUsers(users) {
    const tbody = document.querySelector('#users-table tbody');
    
    if (!users || users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Пользователей нет</td></tr>';
        return;
    }
    
    tbody.innerHTML = users.map(u => `
        <tr>
            <td>${u.login}</td>
            <td>${u.email}</td>
            <td>${u.role}</td>
            <td><span class="status-${u.is_active ? 'norma' : 'overload'}">${u.is_active ? 'Активен' : 'Заблокирован'}</span></td>
            <td>
                <button class="btn btn-warning" onclick="editUser(${u.id})">✏️</button>
                <button class="btn btn-danger" onclick="deleteUser(${u.id})">🗑️</button>
            </td>
        </tr>
    `).join('');
}

function renderMockUsers() {
    const tbody = document.querySelector('#users-table tbody');
    tbody.innerHTML = `
        <tr>
            <td>admin</td>
            <td>admin@asbn.local</td>
            <td>admin</td>
            <td><span class="status-norma">Активен</span></td>
            <td>
                <button class="btn btn-warning">✏️</button>
                <button class="btn btn-danger">🗑️</button>
            </td>
        </tr>
        <tr>
            <td>dispatcher1</td>
            <td>disp@asbn.local</td>
            <td>dispatcher</td>
            <td><span class="status-norma">Активен</span></td>
            <td>
                <button class="btn btn-warning">✏️</button>
                <button class="btn btn-danger">🗑️</button>
            </td>
        </tr>
        <tr>
            <td>analyst1</td>
            <td>anal@asbn.local</td>
            <td>analyst</td>
            <td><span class="status-norma">Активен</span></td>
            <td>
                <button class="btn btn-warning">✏️</button>
                <button class="btn btn-danger">🗑️</button>
            </td>
        </tr>
    `;
}

async function loadSystemStatus() {
    const container = document.getElementById('system-status');
    
    try {
        const status = await api.getSystemStatus();
        container.innerHTML = `
            <div class="grid grid-2">
                <div class="status-card">
                    <div class="status-value">${status.users_count || 3}</div>
                    <div class="status-label">Пользователей</div>
                </div>
                <div class="status-card">
                    <div class="status-value">${status.events_count || 10}</div>
                    <div class="status-label">Событий</div>
                </div>
                <div class="status-card">
                    <div class="status-value">${status.commands_count || 5}</div>
                    <div class="status-label">Команд</div>
                </div>
                <div class="status-card">
                    <div class="status-value" style="color: #48bb78;">${status.database || 'connected'}</div>
                    <div class="status-label">База данных</div>
                </div>
            </div>
            <div class="alert alert-success mt-2">Статус системы: ${status.status || 'operational'}</div>
        `;
    } catch (error) {
        container.innerHTML = '<div class="alert alert-error">Ошибка загрузки статуса</div>';
    }
}

async function loadCommandsLog() {
    try {
        const data = await api.getCommands(20);
        renderCommandsLog(data.commands);
    } catch (error) {
        renderMockCommandsLog();
    }
}

function renderCommandsLog(commands) {
    const tbody = document.querySelector('#commands-log-table tbody');
    
    if (!commands || commands.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">Команд нет</td></tr>';
        return;
    }
    
    tbody.innerHTML = commands.map(c => `
        <tr>
            <td>${new Date(c.sent_at).toLocaleString('ru-RU')}</td>
            <td>${c.command_type}</td>
            <td><code style="font-size: 11px;">${JSON.stringify(c.parameters || {})}</code></td>
            <td><span class="status-norma">${c.status}</span></td>
            <td>#${c.operator_id || '-'}</td>
        </tr>
    `).join('');
}

function renderMockCommandsLog() {
    const tbody = document.querySelector('#commands-log-table tbody');
    tbody.innerHTML = `
        <tr>
            <td>${new Date().toLocaleString('ru-RU')}</td>
            <td>Переключение фидера</td>
            <td><code>{"source": 1, "target": 2}</code></td>
            <td><span class="status-norma">executed</span></td>
            <td>#1</td>
        </tr>
    `;
}

async function loadSystemLogs() {
    const container = document.getElementById('system-logs');
    const logs = [
        `[${new Date().toISOString()}] INFO: Система запущена`,
        `[${new Date(Date.now() - 60000).toISOString()}] INFO: Топология загружена (5 узлов)`,
        `[${new Date(Date.now() - 120000).toISOString()}] INFO: Измерения получены (50 записей)`,
        `[${new Date(Date.now() - 180000).toISOString()}] WARNING: Превышение порога на узле ПС-2`,
        `[${new Date(Date.now() - 240000).toISOString()}] INFO: Прогноз рассчитан (MAPE: 4.2%)`
    ];
    container.innerHTML = logs.join('<br>');
}

function showCreateUser() {
    document.getElementById('create-user-modal').classList.remove('hidden');
}

function closeCreateUser() {
    document.getElementById('create-user-modal').classList.add('hidden');
}

async function createUser() {
    const login = document.getElementById('new-login').value;
    const email = document.getElementById('new-email').value;
    const password = document.getElementById('new-password').value;
    const role = document.getElementById('new-role').value;
    
    if (!login || !email || !password) {
        alert('Заполните все поля');
        return;
    }
    
    try {
        // В прототипе просто показываем успех
        alert(`Пользователь ${login} создан`);
        closeCreateUser();
        loadUsers();
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
}

async function deleteUser(id) {
    if (confirm('Удалить пользователя?')) {
        try {
            await api.request(`/admin/users/${id}`, { method: 'DELETE' });
            loadUsers();
        } catch (error) {
            alert('Пользователь удалён (прототип)');
            loadUsers();
        }
    }
}

function editUser(id) {
    alert('Редактирование пользователя #' + id);
}

async function saveThresholds() {
    const warning = document.getElementById('threshold-warning').value;
    const emergency = document.getElementById('threshold-emergency').value;
    const voltage = document.getElementById('threshold-voltage').value;
    
    alert(`Пороги сохранены:\nПредупреждение: ${warning}%\nАвария: ${emergency}%\nНапряжение: ${voltage}%`);
}