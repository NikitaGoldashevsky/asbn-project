/**
 * АСБН - Логика авторизации
 * Разработчик: Голдашевский Н.С., гр. 4331
 */

// Проверка авторизации
function checkAuth() {
    const token = api.getToken();
    const currentPage = window.location.pathname;
    const isAuthPage = currentPage.includes('login.html') || 
                       currentPage.includes('register.html');

    if (!token && !isAuthPage) {
        window.location.href = 'login.html';
        return false;
    }

    if (token && isAuthPage) {
        window.location.href = 'pages/monitoring.html';
        return false;
    }

    return true;
}

// Выход из системы
function logout() {
    api.clearToken();
    window.location.href = '../login.html';
}

// Получение роли пользователя
function getUserRole() {
    const token = api.getToken();
    if (!token) return null;
    
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.role;
    } catch (e) {
        return null;
    }
}

// Проверка прав доступа
function hasRole(roles) {
    const userRole = getUserRole();
    if (!userRole) return false;
    
    if (Array.isArray(roles)) {
        return roles.includes(userRole);
    }
    return userRole === roles;
}

// Отображение элементов по роли
function showByRole(element, roles) {
    if (hasRole(roles)) {
        element.classList.remove('hidden');
    } else {
        element.classList.add('hidden');
    }
}

// Инициализация навигации
function initNavbar() {
    const role = getUserRole();
    const navbar = document.getElementById('user-navbar');
    
    if (!navbar || !role) return;
    
    // Показываем/скрываем элементы по роли
    const adminLinks = navbar.querySelectorAll('.admin-only');
    const dispatcherLinks = navbar.querySelectorAll('.dispatcher-only');
    
    adminLinks.forEach(el => showByRole(el, 'admin'));
    dispatcherLinks.forEach(el => showByRole(el, ['dispatcher', 'admin']));
    
    // Отображение имени пользователя
    const userNameEl = document.getElementById('user-name');
    if (userNameEl) {
        userNameEl.textContent = `Пользователь (${role})`;
    }
}

// Обработка формы входа
async function handleLogin(event) {
    event.preventDefault();
    
    const loginInput = document.getElementById('login');
    const passwordInput = document.getElementById('password');
    const errorDiv = document.getElementById('login-error');
    
    try {
        const result = await api.login(loginInput.value, passwordInput.value);
        
        // Сохранение токена уже сделано в api.login()
        window.location.href = 'pages/monitoring.html';
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.classList.remove('hidden');
    }
}

// Обработка формы регистрации
async function handleRegister(event) {
    event.preventDefault();
    
    const loginInput = document.getElementById('login');
    const passwordInput = document.getElementById('password');
    const emailInput = document.getElementById('email');
    const errorDiv = document.getElementById('register-error');
    const successDiv = document.getElementById('register-success');
    
    // Валидация пароля
    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,32}$/;
    if (!passwordRegex.test(passwordInput.value)) {
        errorDiv.textContent = 'Пароль должен содержать 8-32 символа, заглавную букву, строчную букву, цифру и спецсимвол (!@#$%^&*)';
        errorDiv.classList.remove('hidden');
        return;
    }
    
    try {
        await api.register(loginInput.value, passwordInput.value, emailInput.value);
        
        errorDiv.classList.add('hidden');
        successDiv.classList.remove('hidden');
        
        // Очистка формы
        loginInput.value = '';
        passwordInput.value = '';
        emailInput.value = '';
        
        // Перенаправление через 2 секунды
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 2000);
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.classList.remove('hidden');
        successDiv.classList.add('hidden');
    }
}

// Экспорт функций
window.checkAuth = checkAuth;
window.logout = logout;
window.getUserRole = getUserRole;
window.hasRole = hasRole;
window.handleLogin = handleLogin;
window.handleRegister = handleRegister;
window.initNavbar = initNavbar;