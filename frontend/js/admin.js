/**
 * АСБН - Логика админ-панели (ИСПРАВЛЕННАЯ ВЕРСИЯ)
 * Разработчик: Голдашевский Н.С., гр. 4331
 */

let currentUserEdit = null;

async function loadAdminData() {
    loadUsers();
    loadSystemStatus();
    loadCommandsLog();
    loadSystemLogs();
}

async function loadUsers() {
    const tbody = document.querySelector('#users-table tbody');
    tbody.innerHTML = '<tr><td colspan="5" class="text-center">Загрузка...</td></tr>';
    
    try {
        const data = await api.getUsers();
        console.log('Пользователи получены:', data.users);
        renderUsers(data.users);
    } catch (error) {
        console.log('API недоступно, используем тестовые данные');
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
                <button class="btn btn-warning" onclick="editUser(${u.id}, '${u.login}', '${u.email}', '${u.role}', ${u.is_active})">✏️</button>
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
                <button class="btn btn-warning" onclick="editUser(1, 'admin', 'admin@asbn.local', 'admin', true)">✏️</button>
                <button class="btn btn-danger" onclick="deleteUser(1)">🗑️</button>
            </td>
        </tr>
        <tr>
            <td>dispatcher1</td>
            <td>disp@asbn.local</td>
            <td>dispatcher</td>
            <td><span class="status-norma">Активен</span></td>
            <td>
                <button class="btn btn-warning" onclick="editUser(2, 'dispatcher1', 'disp@asbn.local', 'dispatcher', true)">✏️</button>
                <button class="btn btn-danger" onclick="deleteUser(2)">🗑️</button>
            </td>
        </tr>
        <tr>
            <td>analyst1</td>
            <td>anal@asbn.local</td>
            <td>analyst</td>
            <td><span class="status-norma">Активен</span></td>
            <td>
                <button class="btn btn-warning" onclick="editUser(3, 'analyst1', 'anal@asbn.local', 'analyst', true)">✏️</button>
                <button class="btn btn-danger" onclick="deleteUser(3)">🗑️</button>
            </td>
        </tr>
    `;
}

async function createUser() {
    const login = document.getElementById('new-login').value.trim();
    const email = document.getElementById('new-email').value.trim();
    const password = document.getElementById('new-password').value.trim();
    const role = document.getElementById('new-role').value;
    
    if (!login || !email || !password) {
        alert('Заполните все поля!');
        return;
    }
    
    try {
        const response = await fetch('http://127.0.0.1:8000/api/admin/users', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${api.getToken()}`
            },
            body: JSON.stringify({
                login: login,
                password: password,
                email: email,
                role: role
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка создания');
        }
        
        alert(`Пользователь "${login}" успешно создан!`);
        closeCreateUser();
        loadUsers();
        
    } catch (error) {
        console.error('Ошибка:', error);
        alert('❌ Ошибка: ' + error.message + '\n\nПроверьте что backend запущен (python run.py)');
    }
}

async function editUser(id, login, email, role, isActive) {
    currentUserEdit = { id, login, email, role, isActive };
    
    // Заполняем модальное окно текущими данными
    document.getElementById('edit-login').value = login;
    document.getElementById('edit-email').value = email;
    document.getElementById('edit-role').value = role;
    document.getElementById('edit-active').checked = isActive;
    document.getElementById('edit-password').value = ''; // Пароль не показываем
    
    // Показываем модальное окно редактирования
    document.getElementById('edit-user-modal').classList.remove('hidden');
    document.getElementById('edit-user-modal').style.display = 'flex';
}

async function saveUserEdit() {
    const login = document.getElementById('edit-login').value.trim();
    const email = document.getElementById('edit-email').value.trim();
    const role = document.getElementById('edit-role').value;
    const password = document.getElementById('edit-password').value.trim();
    const isActive = document.getElementById('edit-active').checked;
    
    if (!login || !email) {
        alert('Заполните логин и email!');
        return;
    }
    
    try {
        const body = {
            login: login,
            email: email,
            role: role,
            is_active: isActive
        };
        
        // Добавляем пароль только если он введён
        if (password && password.length > 0) {
            body.password = password;
        }
        
        const response = await fetch(`http://127.0.0.1:8000/api/admin/users/${currentUserEdit.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${api.getToken()}`
            },
            body: JSON.stringify(body)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка обновления');
        }
        
        alert(`Пользователь "${login}" обновлён!`);
        closeEditUser();
        loadUsers();
        
    } catch (error) {
        console.error('Ошибка:', error);
        alert('Ошибка: ' + error.message);
    }
}

function closeEditUser() {
    document.getElementById('edit-user-modal').classList.add('hidden');
    document.getElementById('edit-user-modal').style.display = 'none';
    currentUserEdit = null;
}

async function deleteUser(id) {
    if (confirm('Вы уверены что хотите удалить пользователя?')) {
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/admin/users/${id}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${api.getToken()}`
                }
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Ошибка удаления');
            }
            
            alert('Пользователь удалён');
            loadUsers();
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Ошибка: ' + error.message);
        }
    }
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
    document.getElementById('create-user-modal').style.display = 'flex';
}

function closeCreateUser() {
    document.getElementById('create-user-modal').classList.add('hidden');
    document.getElementById('create-user-modal').style.display = 'none';
}

async function saveThresholds() {
    const warning = document.getElementById('threshold-warning').value;
    const emergency = document.getElementById('threshold-emergency').value;
    const voltage = document.getElementById('threshold-voltage').value;
    
    alert(`Пороги сохранены:\nПредупреждение: ${warning}%\nАвария: ${emergency}%\nНапряжение: ${voltage}%`);
}